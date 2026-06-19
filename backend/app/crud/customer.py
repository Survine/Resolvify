from sqlalchemy.orm import Session
from typing import List, Optional

from app import models, schemas


def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    db_customer = models.Customer(name=customer.name, email=customer.email)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
    return db.query(models.Customer).offset(skip).limit(limit).all()


def update_customer(
    db: Session, customer_id: int, customer_data: schemas.CustomerUpdate
) -> Optional[models.Customer]:
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    for field, value in customer_data.model_dump(exclude_unset=True).items():
        setattr(db_customer, field, value)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
    return db_customer
