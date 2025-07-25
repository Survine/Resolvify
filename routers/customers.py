from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..schemas.customer import Customer, CustomerCreate
from ..crud.customer import (
    get_customer, get_customer_by_email, get_customers, 
    create_customer, update_customer, delete_customer
)
from ..dependencies import get_db

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=Customer)
def create_new_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_customer(db=db, customer=customer)

@router.get("/", response_model=List[Customer])
def read_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    customers = get_customers(db, skip=skip, limit=limit)
    return customers

@router.get("/{customer_id}", response_model=Customer)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return db_customer

@router.put("/{customer_id}", response_model=Customer)
def update_existing_customer(customer_id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    db_customer = get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if email is being changed to an existing email
    if customer.email != db_customer.email:
        existing_customer = get_customer_by_email(db, email=customer.email)
        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    return update_customer(db=db, customer_id=customer_id, customer_data=customer)

@router.delete("/{customer_id}", response_model=Customer)
def delete_existing_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return delete_customer(db=db, customer_id=customer_id)