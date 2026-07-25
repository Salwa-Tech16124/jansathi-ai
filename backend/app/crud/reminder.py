from sqlalchemy.orm import Session
from app.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate


def get_reminders(db: Session, citizen_id: int = None, status: str = None, skip: int = 0, limit: int = 100):
    query = db.query(Reminder)
    if citizen_id:
        query = query.filter(Reminder.citizen_id == citizen_id)
    if status:
        query = query.filter(Reminder.status == status)
    return query.order_by(Reminder.id.desc()).offset(skip).limit(limit).all()


def get_reminder_by_id(db: Session, reminder_id: int):
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()


def create_reminder(db: Session, reminder: ReminderCreate):
    db_reminder = Reminder(
        citizen_id=reminder.citizen_id,
        scheme_id=reminder.scheme_id,
        title=reminder.title,
        category=reminder.category,
        reminder_date=reminder.reminder_date,
        status=reminder.status or "pending"
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def update_reminder(db: Session, reminder_id: int, reminder_update: ReminderUpdate):
    db_reminder = get_reminder_by_id(db, reminder_id)
    if not db_reminder:
        return None
    
    update_data = reminder_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_reminder, key, value)
    
    db.commit()
    db.refresh(db_reminder)
    return db_reminder


def delete_reminder(db: Session, reminder_id: int):
    db_reminder = get_reminder_by_id(db, reminder_id)
    if db_reminder:
        db.delete(db_reminder)
        db.commit()
        return True
    return False
