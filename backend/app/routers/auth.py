from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import schemas, crud
from app.config import settings
from app.database import get_db
from app.services.auth import authenticate_employee, create_access_token
from app.schemas.auth import Token

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    employee = authenticate_employee(db, form_data.username, form_data.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": employee.username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.Employee)
async def register(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    if crud.get_employee_by_username(db, employee.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    from app import models

    existing = (
        db.query(models.Employee)
        .filter(models.Employee.email == employee.email)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_employee(db=db, employee=employee)
