from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatMessageBase(BaseModel):
    message: str

class ChatMessageCreate(ChatMessageBase):
    session_id: int
    is_from_customer: bool = False

class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    employee_id: Optional[int] = None
    is_from_customer: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
        