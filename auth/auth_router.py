from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import schemas
import models
import crud
from auth.auth import authenticate_employee, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.auth_schema import Token
from databases.database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    employee = authenticate_employee(db, form_data.username, form_data.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": employee.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.Employee)
async def register_employee(
    employee: schemas.EmployeeCreate,
    db: Session = Depends(get_db)
):
    # Check if username already exists
    db_employee = crud.get_employee_by_username(db, employee.username)
    if db_employee:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_employee = db.query(models.Employee).filter(
        models.Employee.email == employee.email
    ).first()
    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    return crud.create_employee(db=db, employee=employee)
