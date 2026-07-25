from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=False)
    required_documents = Column(Text, nullable=False)
    deadline = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
