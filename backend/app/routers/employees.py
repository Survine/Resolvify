from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas, crud
from app.database import get_db
from app.dependencies import employee_read, employee_create, employee_update, employee_delete
from app.services.auth import get_current_active_employee

router = APIRouter(prefix="/employees", tags=["employees"])


@router.post("/", response_model=schemas.Employee)
def create_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db),
    _=Depends(employee_create),
):
    if crud.get_employee_by_username(db, employee.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_employee(db=db, employee=employee)


@router.get("/", response_model=List[schemas.Employee])
def list_employees(
    skip: int = 0,
    limit: int = 100,
    shop_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _=Depends(employee_read),
):
    return crud.get_employees(db, skip=skip, limit=limit, shop_id=shop_id)


@router.get("/me", response_model=schemas.Employee)
def get_me(current=Depends(get_current_active_employee)):
    return current


@router.get("/{employee_id}", response_model=schemas.Employee)
def get_employee(employee_id: int, db: Session = Depends(get_db), _=Depends(employee_read)):
    emp = crud.get_employee(db, employee_id=employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@router.put("/{employee_id}", response_model=schemas.Employee)
def update_employee(
    employee_id: int,
    employee: schemas.EmployeeUpdate,
    db: Session = Depends(get_db),
    _=Depends(employee_update),
):
    result = crud.update_employee(db, employee_id=employee_id, employee=employee)
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result


@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), _=Depends(employee_delete)):
    if not crud.delete_employee(db, employee_id=employee_id):
        raise HTTPException(status_code=404, detail="Employee not found")
    return {"message": "Employee deleted successfully"}
