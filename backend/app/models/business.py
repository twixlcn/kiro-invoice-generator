"""Pydantic v2 schemas for the business domain."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class BusinessBase(BaseModel):
    name: str
    address: str
    email: EmailStr

    @field_validator("name", "address", mode="before")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(BusinessBase):
    pass


class BusinessResponse(BusinessBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
