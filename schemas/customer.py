from pydantic import BaseModel, EmailStr
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    email: EmailStr

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: str = None
    email: EmailStr = None

class Customer(CustomerBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True