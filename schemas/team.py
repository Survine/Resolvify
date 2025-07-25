from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TeamBase(BaseModel):
    name: str
    description: Optional[str] = None

class TeamCreate(TeamBase):
    shop_id: int

class TeamUpdate(TeamBase):
    name: Optional[str] = None

class Team(TeamBase):
    id: int
    shop_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True