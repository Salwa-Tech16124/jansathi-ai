from sqlalchemy.orm import Session
from app.models.citizen import Citizen
from app.schemas.citizen import CitizenCreate


def get_citizens(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Citizen).offset(skip).limit(limit).all()


def get_citizen_by_id(db: Session, citizen_id: int):
    return db.query(Citizen).filter(Citizen.id == citizen_id).first()


def get_citizen_by_phone(db: Session, phone: str):
    return db.query(Citizen).filter(Citizen.phone == phone).first()


def create_citizen(db: Session, citizen: CitizenCreate):
    db_citizen = Citizen(
        name=citizen.name,
        phone=citizen.phone,
        language=citizen.language,
        district=citizen.district,
        state=citizen.state
    )
    db.add(db_citizen)
    db.commit()
    db.refresh(db_citizen)
    return db_citizen
