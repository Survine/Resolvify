from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models
import schemas


def create_chat_session(db: Session, customer_id: int, shop_id: int) -> models.ChatSession:
    db_session = models.ChatSession(customer_id=customer_id, shop_id=shop_id)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_chat_session(db: Session, session_id: int) -> Optional[models.ChatSession]:
    return db.query(models.ChatSession).filter(models.ChatSession.id == session_id).first()

def get_waiting_chat_sessions(db: Session) -> List[models.ChatSession]:
    return db.query(models.ChatSession).filter(models.ChatSession.status == "waiting").all()

def get_waiting_chat_sessions_by_shop(db: Session, shop_id: int) -> List[models.ChatSession]:
    return db.query(models.ChatSession).filter(
        models.ChatSession.status == "waiting",
        models.ChatSession.shop_id == shop_id
    ).all()

def assign_employee_to_session(db: Session, session_id: int, employee_id: int) -> Optional[models.ChatSession]:
    db_session = get_chat_session(db, session_id)
    if db_session:
        db_session.employee_id = employee_id
        db_session.status = "active"
        db.commit()
        db.refresh(db_session)
    return db_session

def create_chat_message(db: Session, message: schemas.ChatMessageCreate, employee_id: Optional[int] = None) -> models.ChatMessage:
    db_message = models.ChatMessage(
        session_id=message.session_id,
        employee_id=employee_id,
        message=message.message,
        is_from_customer=message.is_from_customer
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def close_chat_session(db: Session, session_id: int) -> Optional[models.ChatSession]:
    db_session = get_chat_session(db, session_id)
    if db_session:
        db_session.status = "closed"
        db_session.closed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session