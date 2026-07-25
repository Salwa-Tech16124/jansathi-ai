from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.citizen import CitizenCreate, CitizenRead
from app.crud import citizen as crud_citizen

router = APIRouter(prefix="/citizens", tags=["Citizens"])


@router.get("", response_model=List[CitizenRead])
def read_citizens(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud_citizen.get_citizens(db, skip=skip, limit=limit)


@router.post("", response_model=CitizenRead, status_code=201)
def create_new_citizen(citizen: CitizenCreate, db: Session = Depends(get_db)):
    existing = crud_citizen.get_citizen_by_phone(db, phone=citizen.phone)
    if existing:
        return existing
    return crud_citizen.create_citizen(db, citizen)


@router.get("/{citizen_id}", response_model=CitizenRead)
def read_citizen(citizen_id: int, db: Session = Depends(get_db)):
    db_citizen = crud_citizen.get_citizen_by_id(db, citizen_id)
    if not db_citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")
    return db_citizen
