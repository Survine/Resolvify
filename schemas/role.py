from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from .permission import Permission

class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    permission_ids: Optional[List[int]] = []

class RoleUpdate(RoleBase):
    name: Optional[str] = None
    permission_ids: Optional[List[int]] = None

class Role(RoleBase):
    id: int
    created_at: datetime
    permissions: List[Permission] = []
    
    class Config:
        from_attributes = True