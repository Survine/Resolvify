from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import schemas
import crud
from permissions import employee_read, employee_create, employee_update, employee_delete
from databases.database import get_db
from auth.auth import get_current_active_employee

router = APIRouter(prefix="/employees", tags=["employees"])

@router.post("/", response_model=schemas.Employee)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    current_employee = Depends(employee_create)
):
    # Check if username already exists
    db_employee = crud.get_employee_by_username(db, employee.username)
    if db_employee:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    return crud.create_employee(db=db, employee=employee)

@router.get("/", response_model=List[schemas.Employee])
def read_employees(
    skip: int = 0,
    limit: int = 100,
    shop_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_employee = Depends(employee_read)
):
    return crud.get_employees(db, skip=skip, limit=limit, shop_id=shop_id)

@router.get("/me", response_model=schemas.Employee)
def read_employee_me(current_employee = Depends(get_current_active_employee)):
    return current_employee

@router.get("/{employee_id}", response_model=schemas.Employee)
def read_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(employee_read)
):
    db_employee = crud.get_employee(db, employee_id=employee_id)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.put("/{employee_id}", response_model=schemas.Employee)
def update_employee(
    employee_id: int,
    employee: schemas.EmployeeUpdate,
    db: Session = Depends(get_db),
    current_employee = Depends(employee_update)
):
    db_employee = crud.update_employee(db, employee_id=employee_id, employee=employee)
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    return db_employee

@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_employee = Depends(employee_delete)
):
    success = crud.delete_employee(db, employee_id=employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}
