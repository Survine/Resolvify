from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatMessageBase(BaseModel):
    message: str


class ChatMessageCreate(ChatMessageBase):
    session_id: int
    is_from_customer: bool = False


class ChatMessageUpdate(BaseModel):
    message: Optional[str] = None


class EmployeeInfo(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str

    model_config = {"from_attributes": True}


class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    employee_id: Optional[int] = None
    is_from_customer: bool
    created_at: datetime
    employee: Optional[EmployeeInfo] = None

    model_config = {"from_attributes": True}


class ShopInfo(BaseModel):
    id: int
    name: str
    location: Optional[str] = None

    model_config = {"from_attributes": True}


class CustomerInfo(BaseModel):
    id: int
    name: str
    email: str

    model_config = {"from_attributes": True}


class ChatSessionBase(BaseModel):
    pass


class ChatSessionCreate(ChatSessionBase):
    customer_id: int
    shop_id: int


class ChatSessionUpdate(BaseModel):
    employee_id: Optional[int] = None
    status: Optional[str] = None


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

    model_config = {"from_attributes": True}
