from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.scheme import SchemeRead


class ReminderBase(BaseModel):
    citizen_id: int
    scheme_id: Optional[int] = None
    title: str
    category: Optional[str] = "General"
    reminder_date: str
    status: Optional[str] = "pending"


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    reminder_date: Optional[str] = None
    status: Optional[str] = None


class ReminderRead(ReminderBase):
    id: int
    created_at: Optional[datetime] = None
    scheme: Optional[SchemeRead] = None

    class Config:
        from_attributes = True
