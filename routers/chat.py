from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import asyncio
import schemas
import crud
import models
from permissions import chat_read, chat_create, chat_update
from databases.database import get_db
from auth.auth import get_current_active_employee

router = APIRouter(prefix="/chat", tags=["chat"])

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.employee_connections: Dict[int, WebSocket] = {}
        self.employee_shop_mapping: Dict[int, int] = {}  # employee_id -> shop_id
        self.customer_connections: Dict[str, WebSocket] = {}  # customer_email -> websocket
        self.session_connections: Dict[int, WebSocket] = {}  # session_id -> customer websocket

    async def connect_employee(self, websocket: WebSocket, employee_id: int, shop_id: int):
        await websocket.accept()
        self.employee_connections[employee_id] = websocket
        self.employee_shop_mapping[employee_id] = shop_id

    async def connect_customer(self, websocket: WebSocket, customer_email: str, session_id: int = None):
        await websocket.accept()
        self.customer_connections[customer_email] = websocket
        if session_id:
            self.session_connections[session_id] = websocket

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
        if employee_id in self.employee_connections:
            await self.employee_connections[employee_id].send_text(message)

    async def send_to_customer(self, message: str, customer_email: str):
        if customer_email in self.customer_connections:
            await self.customer_connections[customer_email].send_text(message)
    
    async def send_to_session(self, message: str, session_id: int):
        """Send message to customer via session ID"""
        if session_id in self.session_connections:
            await self.session_connections[session_id].send_text(message)

    async def broadcast_to_employees(self, message: str):
        for connection in self.employee_connections.values():
            await connection.send_text(message)
    
    async def broadcast_to_shop_employees(self, message: str, shop_id: int):
        """Broadcast message only to employees from a specific shop"""
        for employee_id, connection in self.employee_connections.items():
            if self.employee_shop_mapping.get(employee_id) == shop_id:
                await connection.send_text(message)

manager = ConnectionManager()

# REST API endpoints
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
    
    # Notify available employees from that shop about new session
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
    
    # Notify customer that an agent has been assigned
    if session_id in manager.session_connections:
        await manager.send_personal_message(
            json.dumps({
                "type": "agent_assigned",
                "message": f"A support agent has been assigned to help you.",
                "agent_name": current_employee.username
            }),
            manager.session_connections[session_id]
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
    
    # Notify customer that session is closed
    if session_id in manager.session_connections:
        await manager.send_personal_message(
            json.dumps({
                "type": "session_closed",
                "message": "The support session has been ended by the employee. Thank you for contacting us!"
            }),
            manager.session_connections[session_id]
        )
        # Remove the customer connection
        manager.session_connections.pop(session_id, None)
    
    # Notify employees in the shop about session closure
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

# WebSocket endpoints
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
                db = next(get_db())
                session = crud.get_chat_session(db, message_data["session_id"])
                if session and session.customer:
                    # Send message to customer via session
                    await manager.send_to_session(
                        json.dumps({
                            "type": "message",
                            "message": message_data["message"],
                            "from": "support",
                            "timestamp": message_data.get("timestamp")
                        }),
                        session.id
                    )
                
                db.close()
                
    except WebSocketDisconnect:
        manager.disconnect_employee(employee_id)

@router.websocket("/ws/customer/{customer_email}")
async def websocket_customer(websocket: WebSocket, customer_email: str):
    await manager.connect_customer(websocket, customer_email)
    current_session_id = None
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data["type"] == "chat_message":
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
                
                # Send message to assigned employee if any
                if active_session.employee_id:
                    await manager.send_to_employee(
                        json.dumps({
                            "type": "message",
                            "session_id": active_session.id,
                            "message": message_data["message"],
                            "from": "customer",
                            "customer_email": customer_email,
                            "timestamp": message_data.get("timestamp")
                        }),
                        active_session.employee_id
                    )
                else:
                    # Notify employees from the same shop about unassigned message
                    await manager.broadcast_to_shop_employees(
                        json.dumps({
                            "type": "unassigned_message",
                            "session_id": active_session.id,
                            "message": message_data["message"],
                            "customer_email": customer_email,
                            "shop_id": active_session.shop_id,
                            "timestamp": message_data.get("timestamp")
                        }),
                        active_session.shop_id
                    )
                
                db.close()
                
    except WebSocketDisconnect:
        manager.disconnect_customer(customer_email, current_session_id)
