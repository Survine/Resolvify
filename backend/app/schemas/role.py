from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.permission import Permission


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permission_ids: Optional[List[int]] = None


class Role(RoleBase):
    id: int
    created_at: datetime
    permissions: List[Permission] = []

    model_config = {"from_attributes": True}
