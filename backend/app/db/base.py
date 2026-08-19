"""Declarative base shared by all ORM models and Alembic's autogenerate."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
