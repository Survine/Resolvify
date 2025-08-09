from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import redis
import asyncio
from decouple import config
from concurrent.futures import ThreadPoolExecutor
import threading
from datetime import datetime
import schemas
import crud
import models
from permissions import chat_read, chat_create, chat_update
from databases.database import get_db
from auth.auth import get_current_active_employee


router = APIRouter(prefix="/chat", tags=["chat"])


# Redis-enabled ConnectionManager
class ConnectionManager:
    def __init__(self):
        # Local connections
        self.active_connections: Dict[str, WebSocket] = {}
        self.employee_connections: Dict[int, WebSocket] = {}
        self.employee_shop_mapping: Dict[int, int] = {}
        self.customer_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[int, WebSocket] = {}
        
        # Redis setup with environment variables
        redis_host = config('REDIS_HOST', default='localhost')
        redis_port = config('REDIS_PORT', default=6379, cast=int)
        redis_db = config('REDIS_DB', default=0, cast=int)
        
        self.redis_client = redis.Redis(
            host=redis_host, 
            port=redis_port, 
            db=redis_db,
            decode_responses=True
        )
        self.pubsub = self.redis_client.pubsub()
        
        # Subscribe to Redis channels
        self.pubsub.subscribe(['chat_messages', 'session_notifications', 'employee_notifications'])
          # Test Redis connection
        try:
            self.redis_client.ping()
            print(f"✅ Redis connected successfully at {redis_host}:{redis_port}")
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            print("Multi-worker support will not function properly without Redis")
        
        # Start Redis listener
        self.start_redis_listener()

    def start_redis_listener(self):
        """Start Redis listener in background thread with proper event loop"""
        def redis_listener():
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.redis_loop = loop
            
            try:
                for message in self.pubsub.listen():
                    if message['type'] == 'message':
                        print(f"📨 Redis message received on channel: {message['channel']}")
                        # Run the coroutine in the thread's event loop
                        loop.run_until_complete(self.handle_redis_message(message))
            except Exception as e:
                print(f"Redis listener error: {e}")
            finally:
                loop.close()
            
        self.redis_thread = threading.Thread(target=redis_listener, daemon=True)
        self.redis_thread.start()
    
    def shutdown_redis_listener(self):
        """Shutdown Redis listener gracefully"""
        self._redis_running = False
        if self.pubsub:
            self.pubsub.close()
        if self.redis_client:
            self.redis_client.close()

    async def handle_redis_message(self, message):
        """Handle messages received from Redis"""
        try:
            channel = message['channel']
            data = json.loads(message['data'])
            print(f"🔄 Processing Redis message from channel '{channel}': {data}")
            
            if channel == 'chat_messages':
                await self.handle_chat_message_from_redis(data)
            elif channel == 'session_notifications':
                await self.handle_session_notification_from_redis(data)
            elif channel == 'employee_notifications':
                await self.handle_employee_notification_from_redis(data)
                
        except Exception as e:
            print(f"Error handling Redis message: {e}")
            import traceback
            traceback.print_exc()

    async def handle_chat_message_from_redis(self, data):
        """Handle chat messages from Redis"""
        message_type = data.get('target_type')
        target_id = data.get('target_id')
        message_content = data.get('message')
        
        print(f"📬 Attempting to deliver message: type={message_type}, target={target_id}")
        print(f"   Available employee connections: {list(self.employee_connections.keys())}")
        print(f"   Available customer connections: {list(self.customer_connections.keys())}")
        print(f"   Available session connections: {list(self.session_connections.keys())}")
        
        if message_type == 'employee' and target_id in self.employee_connections:
            print(f"✅ Sending to employee {target_id}")
            await self.employee_connections[target_id].send_text(message_content)
        elif message_type == 'customer' and target_id in self.customer_connections:
            print(f"✅ Sending to customer {target_id}")
            await self.customer_connections[target_id].send_text(message_content)
        elif message_type == 'session' and target_id in self.session_connections:
            print(f"✅ Delivering message to session {target_id} locally")
            await self.session_connections[target_id].send_text(message_content)
        else:
            print(f"❌ No matching connection found for {message_type}:{target_id}")

    async def handle_session_notification_from_redis(self, data):
        """Handle session notifications from Redis"""
        notification_type = data.get('notification_type')
        shop_id = data.get('shop_id')
        message_content = data.get('message')
        
        if notification_type == 'broadcast_to_shop':
            await self._local_broadcast_to_shop_employees(message_content, shop_id)

    async def handle_employee_notification_from_redis(self, data):
        """Handle employee notifications from Redis"""
        await self._local_broadcast_to_employees(data.get('message', ''))

    async def connect_employee(self, websocket: WebSocket, employee_id: int, shop_id: int):
        await websocket.accept()
        self.employee_connections[employee_id] = websocket
        self.employee_shop_mapping[employee_id] = shop_id

    async def connect_customer(self, websocket: WebSocket, customer_email: str, session_id: int = None):
        await websocket.accept()
        self.customer_connections[customer_email] = websocket
        if session_id:
            self.session_connections[session_id] = websocket
            print(f"🔗 Session {session_id} immediately mapped to customer WebSocket for {customer_email}")

    def disconnect_employee(self, employee_id: int):
        if employee_id in self.employee_connections:
            del self.employee_connections[employee_id]
        if employee_id in self.employee_shop_mapping:
            del self.employee_shop_mapping[employee_id]

    def disconnect_customer(self, customer_email: str, session_id: int = None):
        if customer_email in self.customer_connections:
            del self.customer_connections[customer_email]
        if session_id and session_id in self.session_connections:
            del self.session_connections[session_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_to_employee(self, message: str, employee_id: int):
        """Send message to employee via Redis (all workers will attempt delivery)"""
        redis_message = {
            'target_type': 'employee',
            'target_id': employee_id,
            'message': message
        }
        self.redis_client.publish('chat_messages', json.dumps(redis_message))

    async def send_to_customer(self, message: str, customer_email: str):
        """Send message to customer via Redis"""
        redis_message = {
            'target_type': 'customer',
            'target_id': customer_email,
            'message': message
        }
        self.redis_client.publish('chat_messages', json.dumps(redis_message))
    
    async def send_to_session(self, message: str, session_id: int):
        """Send message to customer via session ID through Redis"""
        print(f"Publishing message to Redis for session {session_id}")
        redis_message = {
            'target_type': 'session',
            'target_id': session_id,
            'message': message
        }
        self.redis_client.publish('chat_messages', json.dumps(redis_message))

    async def broadcast_to_employees(self, message: str):
        """Broadcast to all employees via Redis"""
        redis_message = {
            'message': message
        }
        self.redis_client.publish('employee_notifications', json.dumps(redis_message))

    async def _local_broadcast_to_employees(self, message: str):
        """Local broadcast to all employees (called by Redis handler)"""
        for connection in self.employee_connections.values():
            try:
                await connection.send_text(message)
            except:
                pass
    
    async def broadcast_to_shop_employees(self, message: str, shop_id: int):
        """Broadcast message to shop employees via Redis"""
        redis_message = {
            'notification_type': 'broadcast_to_shop',
            'shop_id': shop_id,
            'message': message
        }
        self.redis_client.publish('session_notifications', json.dumps(redis_message))

    async def _local_broadcast_to_shop_employees(self, message: str, shop_id: int):
        """Local broadcast to shop employees (called by Redis handler)"""
        for employee_id, connection in self.employee_connections.items():
            if self.employee_shop_mapping.get(employee_id) == shop_id:
                try:
                    await connection.send_text(message)
                except:
                    self.disconnect_employee(employee_id)


manager = ConnectionManager()


# REST API endpoints (remain the same)
@router.get("/shops/", response_model=List[schemas.Shop])
def get_available_shops(db: Session = Depends(get_db)):
    """Get list of shops available for customer support"""
    return crud.get_shops(db)


@router.post("/sessions/", response_model=schemas.ChatSession)
async def create_chat_session(
    customer_email: str,
    shop_id: int,
    db: Session = Depends(get_db)
):
    # Get or create customer
    customer = crud.get_customer_by_email(db, customer_email)
    if not customer:
        customer = crud.create_customer(db, schemas.CustomerCreate(
            name=customer_email.split('@')[0],
            email=customer_email
        ))
    
    # Verify shop exists
    shop = crud.get_shop(db, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    
    # Create chat session for specific shop
    session = crud.create_chat_session(db, customer.id, shop_id)
    
    # Try to immediately map the session to customer's WebSocket if they're connected
    if customer_email in manager.customer_connections:
        manager.session_connections[session.id] = manager.customer_connections[customer_email]
        print(f"🔗 Immediately mapped new session {session.id} to existing customer WebSocket for {customer_email}")
    
    # Notify available employees from that shop about new session via Redis
    await manager.broadcast_to_shop_employees(
        json.dumps({
            "type": "new_session",
            "session_id": session.id,
            "customer_email": customer_email,
            "shop_id": shop_id,
            "shop_name": shop.name
        }),
        shop_id
    )
    
    return session


@router.get("/sessions/waiting", response_model=List[schemas.ChatSession])
def get_waiting_sessions(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(chat_read)
):
    """Get waiting chat sessions for the employee's shop"""
    return crud.get_waiting_chat_sessions_by_shop(db, current_employee.shop_id)


@router.get("/sessions/active", response_model=List[schemas.ChatSession])
def get_active_sessions(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(chat_read)
):
    """Get active chat sessions assigned to current employee"""
    return db.query(models.ChatSession).filter(
        models.ChatSession.employee_id == current_employee.id,
        models.ChatSession.status == "active"
    ).all()


@router.put("/sessions/{session_id}/assign")
async def assign_session_to_employee(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(chat_update)
):
    session = crud.assign_employee_to_session(db, session_id, current_employee.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Notify customer that an agent has been assigned via Redis
    await manager.send_to_session(
        json.dumps({
            "type": "agent_assigned",
            "message": f"A support agent has been assigned to help you.",
            "agent_name": current_employee.username
        }),
        session_id
    )
    
    return {"message": "Session assigned successfully"}


@router.put("/sessions/{session_id}/close")
async def close_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(chat_update)
):
    session = crud.close_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Notify customer that session is closed via Redis
    await manager.send_to_session(
        json.dumps({
            "type": "session_closed",
            "message": "The support session has been ended by the employee. Thank you for contacting us!"
        }),
        session_id
    )
    
    # Remove the customer connection locally
    manager.session_connections.pop(session_id, None)
    
    # Notify employees in the shop about session closure via Redis
    await manager.broadcast_to_shop_employees(
        json.dumps({
            "type": "session_closed",
            "session_id": session_id,
            "customer_email": session.customer.email if session.customer else "Unknown"
        }),
        session.shop_id
    )
    
    return {"message": "Session closed successfully"}


@router.get("/sessions/{session_id}", response_model=schemas.ChatSession)
def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(chat_read)
):
    session = crud.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


# WebSocket endpoints (remain the same, but now use Redis-enabled manager)
@router.websocket("/ws/employee/{employee_id}")
async def websocket_employee(websocket: WebSocket, employee_id: int):
    # Get employee's shop_id from database
    db = next(get_db())
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        await websocket.close(code=1008, reason="Employee not found")
        return
    
    await manager.connect_employee(websocket, employee_id, employee.shop_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data["type"] == "chat_message":
                # Save message to database
                db = next(get_db())
                crud.create_chat_message(
                    db, 
                    schemas.ChatMessageCreate(
                        session_id=message_data["session_id"],
                        message=message_data["message"],
                        is_from_customer=False
                    ),
                    employee_id=employee_id
                )
                
                # Get customer session for this message
                session = crud.get_chat_session(db, message_data["session_id"])
                employee_name = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
                
                if session and session.customer and employee_name:
                    print(f"Sending message via Redis from employee {employee_id} to session {session.id}")
                    
                    # Send message to customer via Redis
                    await manager.send_to_session(
                        json.dumps({
                            "type": "message",
                            "message": message_data["message"],
                            "from": "support",
                            "timestamp": message_data.get("timestamp"),
                            "agent_name": employee_name.username
                        }),
                        session.id
                    )
                else:
                    print(f"Session {message_data['session_id']} not found or has no customer")
                db.close()
                
    except WebSocketDisconnect:
        manager.disconnect_employee(employee_id)


@router.websocket("/ws/customer/{customer_email}")
async def websocket_customer(websocket: WebSocket, customer_email: str):
    await manager.connect_customer(websocket, customer_email)
    current_session_id = None
    
    # Try to find and map any active session for this customer immediately
    try:
        db = next(get_db())
        customer = crud.get_customer_by_email(db, customer_email)
        if customer:
            # Get the most recent active session for this customer
            active_session = db.query(models.ChatSession).filter(
                models.ChatSession.customer_id == customer.id,
                models.ChatSession.status.in_(["waiting", "active"])
            ).order_by(models.ChatSession.created_at.desc()).first()
            
            if active_session:
                current_session_id = active_session.id
                manager.session_connections[active_session.id] = websocket
                print(f"🔗 Auto-mapped session {active_session.id} to customer WebSocket for {customer_email}")
        db.close()
    except Exception as e:
        print(f"Error auto-mapping session: {e}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "session_connect":
                # Handle session connection to establish mapping
                session_id = message_data.get("session_id")
                if session_id:
                    current_session_id = session_id
                    manager.session_connections[session_id] = websocket
                    print(f"Session {session_id} mapped to customer WebSocket for {customer_email}")
                    
            elif message_data["type"] == "chat_message":
                # Save message to database
                db = next(get_db())
                
                # Get or create customer
                customer = crud.get_customer_by_email(db, customer_email)
                if not customer:
                    customer = crud.create_customer(db, schemas.CustomerCreate(
                        name=customer_email.split('@')[0],
                        email=customer_email
                    ))
                
                # Use session_id from message if provided, otherwise find active session
                session_id = message_data.get("session_id")
                if session_id:
                    active_session = crud.get_chat_session(db, session_id)
                    # Store session ID for this connection
                    if active_session and current_session_id != session_id:
                        current_session_id = session_id
                        manager.session_connections[session_id] = websocket
                else:
                    # Fallback: Get most recent active session for this customer
                    active_session = db.query(models.ChatSession).filter(
                        models.ChatSession.customer_id == customer.id,
                        models.ChatSession.status.in_(["waiting", "active"])
                    ).order_by(models.ChatSession.created_at.desc()).first()
                    
                    if active_session:
                        current_session_id = active_session.id
                        manager.session_connections[active_session.id] = websocket
                
                if not active_session:
                    # Session should have been created via REST API
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "No active chat session found. Please refresh the page and start a new chat."
                    }))
                    continue
                
                # Save customer message
                crud.create_chat_message(
                    db,
                    schemas.ChatMessageCreate(
                        session_id=active_session.id,
                        message=message_data["message"],
                        is_from_customer=True
                    )
                )
                
                # Send message to assigned employee if any via Redis
                if active_session.employee_id:
                    await manager.send_to_employee(
                        json.dumps({
                            "type": "message",
                            "session_id": active_session.id,
                            "message": message_data["message"],
                            "from": "customer",
                            "customer_email": customer_email,
                            "customer_name": customer.name,
                            "timestamp": message_data.get("timestamp")
                        }),
                        active_session.employee_id
                    )
                else:
                    # Notify employees from the same shop about unassigned message via Redis
                    await manager.broadcast_to_shop_employees(
                        json.dumps({
                            "type": "unassigned_message",
                            "session_id": active_session.id,
                            "message": message_data["message"],
                            "customer_email": customer_email,
                            "customer_name": customer.name,
                            "shop_id": active_session.shop_id,
                            "timestamp": message_data.get("timestamp")
                        }),
                        active_session.shop_id
                    )
                
                db.close()
                
    except WebSocketDisconnect:
        manager.disconnect_customer(customer_email, current_session_id)
