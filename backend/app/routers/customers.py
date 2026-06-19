from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.dependencies import customer_read, customer_create, customer_update, customer_delete

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Customer)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db),
):
    if crud.get_customer_by_email(db, email=customer.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_customer(db=db, customer=customer)



@router.get("/", response_model=List[schemas.Customer])
def list_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(customer_read),
):
    return crud.get_customers(db, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db), _=Depends(customer_read)):
    customer = crud.get_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=schemas.Customer)
def update_customer(
    customer_id: int,
    customer: schemas.CustomerUpdate,
    db: Session = Depends(get_db),
    _=Depends(customer_update),
):
    result = crud.update_customer(db, customer_id=customer_id, customer_data=customer)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    return result


@router.delete("/{customer_id}", response_model=schemas.Customer)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _=Depends(customer_delete),
):
    customer = crud.get_customer(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return crud.delete_customer(db=db, customer_id=customer_id)
