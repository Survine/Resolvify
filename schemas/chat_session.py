from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .chat_message import ChatMessage

class ChatSessionBase(BaseModel):
    pass

class ChatSessionCreate(ChatSessionBase):
    customer_id: int

class ChatSession(ChatSessionBase):
    id: int
    customer_id: int
    employee_id: Optional[int] = None
    status: str
    created_at: datetime
    closed_at: Optional[datetime] = None
    messages: List[ChatMessage] = []
    
    class Config:
        from_attributes = True