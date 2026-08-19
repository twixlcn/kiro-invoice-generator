"""Business logic for businesses — thin orchestration over the repository."""
import logging

from sqlalchemy.orm import Session

from app.models.business import BusinessCreate, BusinessUpdate
from app.repositories import business_repository
from app.utils.errors import BusinessNotFoundError

logger = logging.getLogger(__name__)


def get_all_businesses(db: Session) -> list:
    return business_repository.list_all(db)


def get_business(db: Session, business_id: int):
    business = business_repository.find(db, business_id)
    if business is None:
        logger.info("Service: business %s not found", business_id)
        raise BusinessNotFoundError(f"Business {business_id} was not found.")
    return business


def create_business(db: Session, data: BusinessCreate):
    business = business_repository.create(db, data.name, data.address, str(data.email))
    logger.debug("Service: created business %s", business.id)
    return business


def update_business(db: Session, business_id: int, data: BusinessUpdate):
    business = get_business(db, business_id)
    business = business_repository.update(db, business, data.name, data.address, str(data.email))
    logger.debug("Service: updated business %s", business_id)
    return business
