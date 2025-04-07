from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CharacterCreate(BaseModel):
    name: str

class CharacterUpdate(BaseModel):
    last_seen_location: Optional[str] = None
    last_login: Optional[datetime] = None

class CharacterOut(CharacterCreate):
    id: int
    name: str
    last_seen_location: str | None = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True
