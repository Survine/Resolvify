from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from .role import Role

class EmployeeBase(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str

class EmployeeCreate(EmployeeBase):
    password: str
    shop_id: int
    role_id: int
    team_ids: Optional[List[int]] = []

class EmployeeUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    shop_id: Optional[int] = None
    role_id: Optional[int] = None
    team_ids: Optional[List[int]] = None

class Employee(EmployeeBase):
    id: int
    is_active: bool
    shop_id: int
    role_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    role: Role
    
    class Config:
        from_attributes = True