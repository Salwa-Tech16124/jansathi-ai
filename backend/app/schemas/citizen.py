from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CitizenBase(BaseModel):
    name: str
    phone: str
    language: Optional[str] = "English"
    district: Optional[str] = None
    state: Optional[str] = None


class CitizenCreate(CitizenBase):
    pass


class CitizenRead(CitizenBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
