from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from decouple import config
import models
from auth.auth_schema import TokenData
from databases.database import get_db

SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM", default="HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(config("ACCESS_TOKEN_EXPIRE_MINUTES", default="30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_employee(db: Session, username: str, password: str) -> Optional[models.Employee]:
    employee = db.query(models.Employee).filter(
        models.Employee.username == username,
        models.Employee.is_active == True
    ).first()
    if not employee:
        return False
    if not verify_password(password, employee.hashed_password):
        return False
    return employee

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_employee(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Employee:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    employee = db.query(models.Employee).filter(
        models.Employee.username == token_data.username,
        models.Employee.is_active == True
    ).first()
    if employee is None:
        raise credentials_exception
    return employee

async def get_current_active_employee(current_employee: models.Employee = Depends(get_current_employee)) -> models.Employee:
    if not current_employee.is_active:
        raise HTTPException(status_code=400, detail="Inactive employee")
    return current_employee
