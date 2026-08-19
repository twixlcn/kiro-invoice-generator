"""Customer API routes — validation, delegation to service, response shaping.

Zero business logic. Zero direct database access.
"""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services import customer_service

router = APIRouter(prefix="/api/customers", tags=["customers"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[CustomerResponse])
async def list_customers(db: Session = Depends(get_db)):
    return customer_service.get_all_customers(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return customer_service.get_customer(db, customer_id)


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(data: CustomerCreate, db: Session = Depends(get_db)):
    return customer_service.create_customer(db, data)


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, data: CustomerUpdate, db: Session = Depends(get_db)):
    return customer_service.update_customer(db, customer_id, data)
