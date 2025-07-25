from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from auth.auth import get_password_hash


def create_employee(db: Session, employee: schemas.EmployeeCreate) -> models.Employee:
    hashed_password = get_password_hash(employee.password)
    db_employee = models.Employee(
        username=employee.username,
        email=employee.email,
        first_name=employee.first_name,
        last_name=employee.last_name,
        hashed_password=hashed_password,
        shop_id=employee.shop_id,
        role_id=employee.role_id
    )
    db.add(db_employee)
    db.commit()
    
    if employee.team_ids:
        teams = db.query(models.Team).filter(
            models.Team.id.in_(employee.team_ids)
        ).all()
        db_employee.teams = teams
        db.commit()
    
    db.refresh(db_employee)
    return db_employee

def get_employee(db: Session, employee_id: int) -> Optional[models.Employee]:
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()

def get_employee_by_username(db: Session, username: str) -> Optional[models.Employee]:
    return db.query(models.Employee).filter(models.Employee.username == username).first()

def get_employees(db: Session, skip: int = 0, limit: int = 100, shop_id: Optional[int] = None) -> List[models.Employee]:
    query = db.query(models.Employee)
    if shop_id:
        query = query.filter(models.Employee.shop_id == shop_id)
    return query.offset(skip).limit(limit).all()

def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeUpdate) -> Optional[models.Employee]:
    db_employee = get_employee(db, employee_id)
    if db_employee:
        update_data = employee.dict(exclude_unset=True, exclude={'team_ids'})
        for field, value in update_data.items():
            setattr(db_employee, field, value)
        
        if employee.team_ids is not None:
            teams = db.query(models.Team).filter(
                models.Team.id.in_(employee.team_ids)
            ).all()
            db_employee.teams = teams
        
        db.commit()
        db.refresh(db_employee)
    return db_employee

def delete_employee(db: Session, employee_id: int) -> bool:
    db_employee = get_employee(db, employee_id)
    if db_employee:
        db.delete(db_employee)
        db.commit()
        return True
    return False