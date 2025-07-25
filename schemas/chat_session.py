from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .chat_message import ChatMessage

class ChatSessionBase(BaseModel):
    pass

class ChatSessionCreate(ChatSessionBase):
    customer_id: int
    shop_id: int

class ChatSessionUpdate(BaseModel):
    employee_id: Optional[int] = None
    status: Optional[str] = None

class ShopInfo(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    
    class Config:
        from_attributes = True

class CustomerInfo(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True

class ChatSession(ChatSessionBase):
    id: int
    customer_id: int
    shop_id: int
    employee_id: Optional[int] = None
    status: str
    created_at: datetime
    closed_at: Optional[datetime] = None
    messages: List[ChatMessage] = []
    shop: Optional[ShopInfo] = None
    customer: Optional[CustomerInfo] = None
    
    class Config:
        from_attributes = True