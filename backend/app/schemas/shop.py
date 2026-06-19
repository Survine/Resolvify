from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ShopBase(BaseModel):
    name: str
    location: Optional[str] = None


class ShopCreate(ShopBase):
    pass


class ShopUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class Shop(ShopBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
