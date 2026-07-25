from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(Integer, ForeignKey("citizens.id"), nullable=False, index=True)
    scheme_id = Column(Integer, ForeignKey("schemes.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="General")
    reminder_date = Column(String(50), nullable=False)
    status = Column(String(50), default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    citizen = relationship("Citizen", backref="reminders")
    scheme = relationship("Scheme", backref="reminders")
