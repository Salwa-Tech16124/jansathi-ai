from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from app.database import get_db
from app.schemas.scheme import SchemeCreate, SchemeRead
from app.crud import scheme as crud_scheme
from app.services.scheme_collector import scheme_collector
from app.models.scheme import Scheme

router = APIRouter(prefix="/schemes", tags=["Schemes"])


@router.post("/sync", response_model=Dict[str, Any])
def sync_latest_schemes_endpoint(db: Session = Depends(get_db)):
    """
    On-demand endpoint to trigger automated daily government scheme ingestion into SQLite database.
    """
    return scheme_collector.sync_latest_schemes(db)


@router.get("/sync-status", response_model=Dict[str, Any])
def get_sync_status(db: Session = Depends(get_db)):
    """
    Get current government schemes database total count and last sync timestamp.
    """
    total_schemes = db.query(Scheme).count()
    return {
        "status": "online",
        "total_schemes_in_db": total_schemes,
        "last_sync_time": scheme_collector.last_sync_time or "Initialized on Startup",
        "auto_sync_interval": "24 Hours (Daily)"
    }


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
