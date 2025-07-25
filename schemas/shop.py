from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ShopBase(BaseModel):
    name: str
    location: Optional[str] = None

class ShopCreate(ShopBase):
    pass

class ShopUpdate(ShopBase):
    name: Optional[str] = None

class Shop(ShopBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True