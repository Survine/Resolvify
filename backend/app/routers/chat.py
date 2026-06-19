import json
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app import schemas, crud, models
from app.database import get_db
from app.dependencies import chat_read, chat_update
from app.services.chat import ConnectionManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

manager = ConnectionManager()


@router.get("/shops/", response_model=List[schemas.Shop])
def get_available_shops(db: Session = Depends(get_db)):
    return crud.get_shops(db)


@router.post("/sessions/", response_model=schemas.ChatSession)
async def create_chat_session(
    customer_email: str,
    shop_id: int,
    db: Session = Depends(get_db),
):
    customer = crud.get_customer_by_email(db, customer_email)
    if not customer:
        customer = crud.create_customer(
            db,
            schemas.CustomerCreate(name=customer_email.split("@")[0], email=customer_email),
        )

    shop = crud.get_shop(db, shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    session = crud.create_chat_session(db, customer.id, shop_id)

    if customer_email in manager.customer_connections:
        manager.session_connections[session.id] = manager.customer_connections[customer_email]

    await manager.broadcast_to_shop_employees(
        json.dumps({
            "type": "new_session",
            "session_id": session.id,
            "customer_email": customer_email,
            "shop_id": shop_id,
            "shop_name": shop.name,
        }),
        shop_id,
    )
    return session


@router.get("/sessions/waiting", response_model=List[schemas.ChatSession])
def get_waiting_sessions(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(chat_read),
):
    return crud.get_waiting_chat_sessions_by_shop(db, current_employee.shop_id)


@router.get("/sessions/active", response_model=List[schemas.ChatSession])
def get_active_sessions(
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(chat_read),
):
    return (
        db.query(models.ChatSession)
        .filter(
            models.ChatSession.employee_id == current_employee.id,
            models.ChatSession.status == "active",
        )
        .all()
    )


@router.put("/sessions/{session_id}/assign")
async def assign_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee=Depends(chat_update),
):
    session = crud.assign_employee_to_session(db, session_id, current_employee.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    await manager.send_to_session(
        json.dumps({
            "type": "agent_assigned",
            "message": "A support agent has been assigned to help you.",
            "agent_name": current_employee.username,
        }),
        session_id,
    )
    return {"message": "Session assigned successfully"}


@router.put("/sessions/{session_id}/close")
async def close_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_employee=Depends(chat_update),
):
    session = crud.close_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    await manager.send_to_session(
        json.dumps({
            "type": "session_closed",
            "message": "The support session has been ended. Thank you for contacting us!",
        }),
        session_id,
    )
    manager.session_connections.pop(session_id, None)

    await manager.broadcast_to_shop_employees(
        json.dumps({
            "type": "session_closed",
            "session_id": session_id,
            "customer_email": session.customer.email if session.customer else "Unknown",
        }),
        session.shop_id,
    )
    return {"message": "Session closed successfully"}


@router.get("/sessions/{session_id}", response_model=schemas.ChatSession)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    _=Depends(chat_read),
):
    session = crud.get_chat_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.websocket("/ws/employee/{employee_id}")
async def ws_employee(websocket: WebSocket, employee_id: int):
    db = next(get_db())
    employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if not employee:
        await websocket.close(code=1008, reason="Employee not found")
        return

    await manager.connect_employee(websocket, employee_id, employee.shop_id)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg["type"] == "chat_message":
                db = next(get_db())
                crud.create_chat_message(
                    db,
                    schemas.ChatMessageCreate(
                        session_id=msg["session_id"],
                        message=msg["message"],
                        is_from_customer=False,
                    ),
                    employee_id=employee_id,
                )

                session = crud.get_chat_session(db, msg["session_id"])
                emp = db.query(models.Employee).filter(models.Employee.id == employee_id).first()

                if session and session.customer and emp:
                    await manager.send_to_session(
                        json.dumps({
                            "type": "message",
                            "message": msg["message"],
                            "from": "support",
                            "timestamp": msg.get("timestamp"),
                            "agent_name": emp.username,
                        }),
                        session.id,
                    )
                db.close()
    except WebSocketDisconnect:
        manager.disconnect_employee(employee_id)


@router.websocket("/ws/customer/{customer_email}")
async def ws_customer(websocket: WebSocket, customer_email: str):
    await manager.connect_customer(websocket, customer_email)
    current_session_id = None

    try:
        db = next(get_db())
        customer = crud.get_customer_by_email(db, customer_email)
        if customer:
            active = (
                db.query(models.ChatSession)
                .filter(
                    models.ChatSession.customer_id == customer.id,
                    models.ChatSession.status.in_(["waiting", "active"]),
                )
                .order_by(models.ChatSession.created_at.desc())
                .first()
            )
            if active:
                current_session_id = active.id
                manager.session_connections[active.id] = websocket
        db.close()
    except Exception as exc:
        logger.warning("Error auto-mapping session: %s", exc)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg["type"] == "session_connect":
                sid = msg.get("session_id")
                if sid:
                    current_session_id = sid
                    manager.session_connections[sid] = websocket

            elif msg["type"] == "chat_message":
                db = next(get_db())
                customer = crud.get_customer_by_email(db, customer_email)
                if not customer:
                    customer = crud.create_customer(
                        db,
                        schemas.CustomerCreate(
                            name=customer_email.split("@")[0], email=customer_email
                        ),
                    )

                sid = msg.get("session_id")
                active_session = None
                if sid:
                    active_session = crud.get_chat_session(db, sid)
                    if active_session and current_session_id != sid:
                        current_session_id = sid
                        manager.session_connections[sid] = websocket
                else:
                    active_session = (
                        db.query(models.ChatSession)
                        .filter(
                            models.ChatSession.customer_id == customer.id,
                            models.ChatSession.status.in_(["waiting", "active"]),
                        )
                        .order_by(models.ChatSession.created_at.desc())
                        .first()
                    )
                    if active_session:
                        current_session_id = active_session.id
                        manager.session_connections[active_session.id] = websocket

                if not active_session:
                    await websocket.send_text(
                        json.dumps({
                            "type": "error",
                            "message": "No active chat session found. Please start a new chat.",
                        })
                    )
                    continue

                crud.create_chat_message(
                    db,
                    schemas.ChatMessageCreate(
                        session_id=active_session.id,
                        message=msg["message"],
                        is_from_customer=True,
                    ),
                )

                payload = json.dumps({
                    "type": "message" if active_session.employee_id else "unassigned_message",
                    "session_id": active_session.id,
                    "message": msg["message"],
                    "from": "customer",
                    "customer_email": customer_email,
                    "customer_name": customer.name,
                    "timestamp": msg.get("timestamp"),
                    "shop_id": active_session.shop_id,
                })

                if active_session.employee_id:
                    await manager.send_to_employee(payload, active_session.employee_id)
                else:
                    await manager.broadcast_to_shop_employees(payload, active_session.shop_id)

                db.close()

    except WebSocketDisconnect:
        manager.disconnect_customer(customer_email, current_session_id)
