from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.database import get_db
from app.schemas.auth import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def authenticate_employee(db: Session, username: str, password: str):
    from app import models


    employee = (
        db.query(models.Employee)
        .filter(models.Employee.username == username, models.Employee.is_active == True)
        .first()
    )

    if not employee:
        return None
    val = verify_password(password, employee.hashed_password)

    if not val:
        return None
    return employee


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


async def get_current_employee(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    from app import models

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    from sqlalchemy.orm import joinedload

    employee = (
        db.query(models.Employee)
        .options(joinedload(models.Employee.role), joinedload(models.Employee.shop))
        .filter(
            models.Employee.username == token_data.username,
            models.Employee.is_active == True,
        )
        .first()
    )
    if employee is None:
        raise credentials_exception
    return employee


async def get_current_active_employee(
    current_employee=Depends(get_current_employee),
):
    if not current_employee.is_active:
        raise HTTPException(status_code=400, detail="Inactive employee")
    return current_employee
