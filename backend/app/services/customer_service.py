"""Business logic for customers — thin orchestration over the repository."""
import logging

from sqlalchemy.orm import Session

from app.models.customer import CustomerCreate, CustomerUpdate
from app.repositories import customer_repository
from app.utils.errors import CustomerNotFoundError

logger = logging.getLogger(__name__)


def get_all_customers(db: Session) -> list:
    return customer_repository.list_all(db)


def get_customer(db: Session, customer_id: int):
    customer = customer_repository.find(db, customer_id)
    if customer is None:
        logger.info("Service: customer %s not found", customer_id)
        raise CustomerNotFoundError(f"Customer {customer_id} was not found.")
    return customer


def create_customer(db: Session, data: CustomerCreate):
    customer = customer_repository.create(db, data.name, str(data.email))
    logger.debug("Service: created customer %s", customer.id)
    return customer


def update_customer(db: Session, customer_id: int, data: CustomerUpdate):
    customer = get_customer(db, customer_id)
    customer = customer_repository.update(db, customer, data.name, str(data.email))
    logger.debug("Service: updated customer %s", customer_id)
    return customer
