from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.reminder import ReminderCreate, ReminderUpdate, ReminderRead
from app.crud import reminder as crud_reminder

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get("", response_model=List[ReminderRead])
def read_reminders(
    citizen_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud_reminder.get_reminders(db, citizen_id=citizen_id, status=status, skip=skip, limit=limit)


@router.post("", response_model=ReminderRead, status_code=201)
def create_new_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    return crud_reminder.create_reminder(db, reminder)


@router.get("/{reminder_id}", response_model=ReminderRead)
def read_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = crud_reminder.get_reminder_by_id(db, reminder_id)
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder


@router.patch("/{reminder_id}", response_model=ReminderRead)
def update_existing_reminder(reminder_id: int, reminder_update: ReminderUpdate, db: Session = Depends(get_db)):
    db_reminder = crud_reminder.update_reminder(db, reminder_id, reminder_update)
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return db_reminder


@router.delete("/{reminder_id}", status_code=204)
def delete_existing_reminder(reminder_id: int, db: Session = Depends(get_db)):
    success = crud_reminder.delete_reminder(db, reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return None
