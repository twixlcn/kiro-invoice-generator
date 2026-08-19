"""Business persistence — the only place that queries the businesses table.

Functions take a SQLAlchemy Session and plain values; no HTTP concerns,
no business rules beyond what SQL/ORM constraints enforce.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Business


def list_all(db: Session) -> list[Business]:
    return db.query(Business).order_by(Business.id).all()


def find(db: Session, business_id: int) -> Optional[Business]:
    return db.get(Business, business_id)


def create(db: Session, name: str, address: str, email: str) -> Business:
    business = Business(name=name, address=address, email=email)
    db.add(business)
    db.commit()
    db.refresh(business)
    return business


def update(db: Session, business: Business, name: str, address: str, email: str) -> Business:
    business.name = name
    business.address = address
    business.email = email
    db.commit()
    db.refresh(business)
    return business
