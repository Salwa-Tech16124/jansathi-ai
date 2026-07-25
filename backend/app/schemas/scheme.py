from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SchemeBase(BaseModel):
    title: str
    category: str
    description: str
    eligibility: str
    required_documents: str
    deadline: Optional[str] = "Open Year Round"


class SchemeCreate(SchemeBase):
    pass


class SchemeRead(SchemeBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
