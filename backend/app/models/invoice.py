"""Pydantic v2 models for the invoice domain."""
import re
from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.business import BusinessResponse
from app.models.customer import CustomerResponse

INVOICE_NUMBER_RE = re.compile(r"^INV-\d{4,}$")


class InvoiceItem(BaseModel):
    description: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    item_total: float = Field(default=0.0, ge=0)

    @field_validator("description", mode="before")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Description must not be empty")
        return v.strip()


class InvoiceTotals(BaseModel):
    subtotal: float
    discount: float
    taxable_amount: float
    tax: float
    total: float


class InvoiceCreate(BaseModel):
    invoice_number: str
    invoice_date: date
    due_date: date
    business_id: int
    customer_id: int
    items: List[InvoiceItem] = Field(..., min_length=1)
    discount: float = Field(default=0.0, ge=0)
    tax_rate: float = Field(..., ge=0, le=1)
    notes: str | None = None
    payment_method: str | None = None

    @field_validator("invoice_number", mode="before")
    @classmethod
    def valid_invoice_number(cls, v: str) -> str:
        if not isinstance(v, str) or not INVOICE_NUMBER_RE.match(v):
            raise ValueError("invoice_number must match INV-NNNN (4+ digits)")
        return v

    @field_validator("notes", "payment_method", mode="before")
    @classmethod
    def strip_optional_text(cls, v: str | None) -> str | None:
        if v is None:
            return None
        if not isinstance(v, str):
            v = str(v)
        cleaned = v.strip()
        return cleaned or None

    @model_validator(mode="after")
    def due_date_not_before_invoice_date(self) -> "InvoiceCreate":
        if self.due_date < self.invoice_date:
            raise ValueError("due_date must not be earlier than invoice_date")
        return self


class InvoiceResponse(BaseModel):
    invoice_number: str
    invoice_date: date
    due_date: date
    business: BusinessResponse
    customer: CustomerResponse
    items: List[InvoiceItem]
    discount: float
    tax_rate: float
    notes: str | None = None
    payment_method: str | None = None
    totals: InvoiceTotals
    created_at: datetime
    updated_at: datetime


class InvoiceSummary(BaseModel):
    invoice_number: str
    customer_name: str
    total: float
    created_at: datetime
