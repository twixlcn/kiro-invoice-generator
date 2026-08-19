"""Business API routes — validation, delegation to service, response shaping.

Zero business logic. Zero direct database access.
"""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.business import BusinessCreate, BusinessResponse, BusinessUpdate
from app.services import business_service

router = APIRouter(prefix="/api/businesses", tags=["businesses"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[BusinessResponse])
async def list_businesses(db: Session = Depends(get_db)):
    return business_service.get_all_businesses(db)


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: int, db: Session = Depends(get_db)):
    return business_service.get_business(db, business_id)


@router.post("", response_model=BusinessResponse, status_code=201)
async def create_business(data: BusinessCreate, db: Session = Depends(get_db)):
    return business_service.create_business(db, data)


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(business_id: int, data: BusinessUpdate, db: Session = Depends(get_db)):
    return business_service.update_business(db, business_id, data)
