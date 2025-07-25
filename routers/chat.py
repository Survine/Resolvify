from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json
import asyncio
import schemas

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
        self.customer_connections: Dict[str, WebSocket] = {}

    async def connect_employee(self, websocket: WebSocket, employee_id: int):
        await websocket.accept()
        self.employee_connections[employee_id] = websocket

    async def connect_customer(self, websocket: WebSocket, customer_email: str):
        await websocket.accept()
        self.customer_connections[customer_email] = websocket

    def disconnect_employee(self, employee_id: int):
        if employee_id in self.employee_connections:
            del self.employee_connections[employee_id]

    def disconnect_customer(self, customer_email: str):
        if customer_email in self.customer_connections:
            del self.customer_connections[customer_email]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_to_employee(self, message: str, employee_id: int):
        if employee_id in self.employee_connections:
            await self.employee_connections[employee_id].send_text(message)

    async def send_to_customer(self, message: str, customer_email: str):
        if customer_email in self.customer_connections:
            await self.customer_connections[customer_email].send_text(message)

    async def broadcast_to_employees(self, message: str):
        for connection in self.employee_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

# REST API endpoints
@router.post("/sessions/", response_model=schemas.ChatSession)
def create_chat_session(
    customer_email: str,
    db: Session = Depends(get_db)
):
    # Get or create customer
    customer = crud.get_customer_by_email(db, customer_email)
    if not customer:
        customer = crud.create_customer(db, schemas.CustomerCreate(
            name=customer_email.split('@')[0],
            email=customer_email
        ))
    
    # Create chat session
    session = crud.create_chat_session(db, customer.id)
    
    # Notify available employees about new session
    asyncio.create_task(manager.broadcast_to_employees(
        json.dumps({
            "type": "new_session",
            "session_id": session.id,
            "customer_email": customer_email
        })
    ))
    
    return session

@router.get("/sessions/waiting", response_model=List[schemas.ChatSession])
def get_waiting_sessions(
    db: Session = Depends(get_db),
    current_employee = Depends(chat_read)
):
    return crud.get_waiting_chat_sessions(db)

@router.put("/sessions/{session_id}/assign")
def assign_session_to_employee(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(chat_update)
):
    session = crud.assign_employee_to_session(db, session_id, current_employee.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return {"message": "Session assigned successfully"}

@router.put("/sessions/{session_id}/close")
def close_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(chat_update)
):
    session = crud.close_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
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
    await manager.connect_employee(websocket, employee_id)
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
                
                # Get customer email for this session
                session = crud.get_chat_session(db, message_data["session_id"])
                if session and session.customer:
                    # Send message to customer
                    await manager.send_to_customer(
                        json.dumps({
                            "type": "message",
                            "message": message_data["message"],
                            "from": "support",
                            "timestamp": message_data.get("timestamp")
                        }),
                        session.customer.email
                    )
                
                db.close()
                
    except WebSocketDisconnect:
        manager.disconnect_employee(employee_id)

@router.websocket("/ws/customer/{customer_email}")
async def websocket_customer(websocket: WebSocket, customer_email: str):
    await manager.connect_customer(websocket, customer_email)
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
                
                # Get active session or create new one
                active_session = db.query(models.ChatSession).filter(
                    models.ChatSession.customer_id == customer.id,
                    models.ChatSession.status.in_(["waiting", "active"])
                ).first()
                
                if not active_session:
                    active_session = crud.create_chat_session(db, customer.id)
                    # Notify employees about new session
                    await manager.broadcast_to_employees(
                        json.dumps({
                            "type": "new_session",
                            "session_id": active_session.id,
                            "customer_email": customer_email
                        })
                    )
                
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
                    # Notify all employees about unassigned message
                    await manager.broadcast_to_employees(
                        json.dumps({
                            "type": "unassigned_message",
                            "session_id": active_session.id,
                            "message": message_data["message"],
                            "customer_email": customer_email,
                            "timestamp": message_data.get("timestamp")
                        })
                    )
                
                db.close()
                
    except WebSocketDisconnect:
        manager.disconnect_customer(customer_email)
