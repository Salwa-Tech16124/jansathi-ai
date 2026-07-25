from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.scheme import SchemeCreate, SchemeRead
from app.crud import scheme as crud_scheme

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.get("", response_model=List[SchemeRead])
def read_schemes(
    category: Optional[str] = Query(None, description="Filter by category (Scholarships, Farmers, Women, Senior Citizens, Health)"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return crud_scheme.get_schemes(db, category=category, skip=skip, limit=limit)


@router.get("/{scheme_id}", response_model=SchemeRead)
def read_scheme(scheme_id: int, db: Session = Depends(get_db)):
    db_scheme = crud_scheme.get_scheme_by_id(db, scheme_id)
    if not db_scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return db_scheme


@router.post("", response_model=SchemeRead, status_code=201)
def create_new_scheme(scheme: SchemeCreate, db: Session = Depends(get_db)):
    return crud_scheme.create_scheme(db, scheme)
