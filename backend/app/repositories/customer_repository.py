"""Customer persistence — the only place that queries the customers table.

Functions take a SQLAlchemy Session and plain values; no HTTP concerns,
no business rules beyond what SQL/ORM constraints enforce.
"""
from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Customer


def list_all(db: Session) -> list[Customer]:
    return db.query(Customer).order_by(Customer.id).all()


def find(db: Session, customer_id: int) -> Optional[Customer]:
    return db.get(Customer, customer_id)


def create(db: Session, name: str, email: str) -> Customer:
    customer = Customer(name=name, email=email)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def update(db: Session, customer: Customer, name: str, email: str) -> Customer:
    customer.name = name
    customer.email = email
    db.commit()
    db.refresh(customer)
    return customer
