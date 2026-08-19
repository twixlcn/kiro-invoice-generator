"""One-time migration: import backend/data/INV-*.json into PostgreSQL.

Reuses an existing Business/Customer row when the JSON data matches one
already in the database (exact name/address/email or name/email match).
Skips any invoice_number already present, so reruns are safe.

Run from the backend/ directory: python scripts/migrate_json_to_db.py
"""
import json
import sys
from datetime import date
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import DATA_DIR
from app.db.models import Business, Customer, Invoice, InvoiceItem
from app.db.session import SessionLocal


def _find_or_create_business(db, name: str, address: str, email: str) -> Business:
    business = (
        db.query(Business)
        .filter(Business.name == name, Business.address == address, Business.email == email)
        .first()
    )
    if business is not None:
        return business
    business = Business(name=name, address=address, email=email)
    db.add(business)
    db.flush()
    return business


def _find_or_create_customer(db, name: str, email: str) -> Customer:
    customer = db.query(Customer).filter(Customer.name == name, Customer.email == email).first()
    if customer is not None:
        return customer
    customer = Customer(name=name, email=email)
    db.add(customer)
    db.flush()
    return customer


def migrate_invoice(db, data: dict) -> Optional[Invoice]:
    """Migrate a single invoice dict. Returns the created Invoice, or None if
    an invoice with this invoice_number already exists."""
    invoice_number = data["invoice_number"]
    existing = db.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
    if existing is not None:
        return None

    business = _find_or_create_business(
        db, data["business"]["name"], data["business"]["address"], data["business"]["email"]
    )
    customer = _find_or_create_customer(db, data["customer"]["name"], data["customer"]["email"])

    totals = data["totals"]
    invoice = Invoice(
        invoice_number=invoice_number,
        business_id=business.id,
        customer_id=customer.id,
        invoice_date=date.fromisoformat(data["invoice_date"]),
        due_date=date.fromisoformat(data["due_date"]),
        discount=data["discount"],
        tax_rate=data["tax_rate"],
        subtotal=totals["subtotal"],
        taxable_amount=totals["taxable_amount"],
        tax=totals["tax"],
        total=totals["total"],
    )
    invoice.items = [
        InvoiceItem(
            description=item["description"],
            quantity=item["quantity"],
            unit_price=item["unit_price"],
            item_total=item["item_total"],
        )
        for item in data["items"]
    ]
    db.add(invoice)
    db.commit()
    return invoice


def migrate() -> None:
    db = SessionLocal()
    try:
        files = sorted(DATA_DIR.glob("INV-*.json"))
        print(f"Found {len(files)} JSON invoice(s) in {DATA_DIR}")
        for filepath in files:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            result = migrate_invoice(db, data)
            if result is None:
                print(f"  {data['invoice_number']}: already migrated, skipping")
            else:
                print(f"  {result.invoice_number}: migrated")
        print("Migration complete.")
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
