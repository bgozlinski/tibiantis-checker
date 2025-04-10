from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CharacterCreate(BaseModel):
    name: str

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    last_seen_location: Optional[str] = None
    last_login: Optional[datetime] = None
    level: Optional[int] = None
    vocation: Optional[str] = None

class CharacterOut(BaseModel):
    id: int
    name: str
    last_seen_location: Optional[str] = None
    last_login: Optional[datetime] = None
    level: Optional[int] = None
    vocation: Optional[str] = None

    class Config:
        from_attributes = True
