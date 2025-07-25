from sqlalchemy.orm import Session
from ..models.customer import Customer as CustomerModel
from ..schemas.customer import CustomerCreate

def get_customer(db: Session, customer_id: int):
    return db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()

def get_customer_by_email(db: Session, email: str):
    return db.query(CustomerModel).filter(CustomerModel.email == email).first()

def get_customers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CustomerModel).offset(skip).limit(limit).all()

def create_customer(db: Session, customer: CustomerCreate):
    db_customer = CustomerModel(
        name=customer.name,
        email=customer.email
    )
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

def update_customer(db: Session, customer_id: int, customer_data: CustomerCreate):
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if db_customer:
        db_customer.name = customer_data.name
        db_customer.email = customer_data.email
        db.commit()
        db.refresh(db_customer)
    return db_customer

def delete_customer(db: Session, customer_id: int):
    db_customer = db.query(CustomerModel).filter(CustomerModel.id == customer_id).first()
    if db_customer:
        db.delete(db_customer)
        db.commit()
    return db_customer