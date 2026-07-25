from sqlalchemy.orm import Session
from app.models.scheme import Scheme
from app.schemas.scheme import SchemeCreate


def get_schemes(db: Session, category: str = None, skip: int = 0, limit: int = 100):
    query = db.query(Scheme)
    if category:
        query = query.filter(Scheme.category.ilike(f"%{category}%"))
    return query.offset(skip).limit(limit).all()


def get_scheme_by_id(db: Session, scheme_id: int):
    return db.query(Scheme).filter(Scheme.id == scheme_id).first()


def create_scheme(db: Session, scheme: SchemeCreate):
    db_scheme = Scheme(
        title=scheme.title,
        category=scheme.category,
        description=scheme.description,
        eligibility=scheme.eligibility,
        required_documents=scheme.required_documents,
        deadline=scheme.deadline
    )
    db.add(db_scheme)
    db.commit()
    db.refresh(db_scheme)
    return db_scheme
