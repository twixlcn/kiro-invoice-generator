"""Pydantic v2 schemas for the customer domain."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class CustomerBase(BaseModel):
    name: str
    email: EmailStr

    @field_validator("name", mode="before")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Field must not be empty")
        return v.strip()


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
