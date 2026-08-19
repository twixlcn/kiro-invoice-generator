"""Integration tests for invoice API endpoints, backed by PostgreSQL.

Uses the `client`/`db_session` fixtures from conftest.py — a real Postgres
test database (invoices_test), isolated per test via a rolled-back
transaction. No live server required — TestClient from httpx.
"""
import pytest


@pytest.fixture
def business(client):
    r = client.post("/api/businesses", json={
        "name": "ACME Digital Solutions",
        "address": "Davao City, Philippines",
        "email": "hello@acmedigital.com",
    })
    return r.json()


@pytest.fixture
def customer(client):
    r = client.post("/api/customers", json={
        "name": "Juan Dela Cruz",
        "email": "juan@example.com",
    })
    return r.json()


@pytest.fixture
def payload(business, customer):
    return {
        "invoice_number": "INV-0001",
        "invoice_date": "2026-08-16",
        "due_date": "2026-08-30",
        "business_id": business["id"],
        "customer_id": customer["id"],
        "items": [
            {"description": "Web Design", "quantity": 1, "unit_price": 15000},
            {"description": "Website Hosting", "quantity": 2, "unit_price": 1000},
        ],
        "discount": 1000,
        "tax_rate": 0.12,
    }


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["invoice_count"] == 0


# ---------------------------------------------------------------------------
# Calculate
# ---------------------------------------------------------------------------
def test_calculate(client, payload):
    r = client.post("/api/invoices/calculate", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["subtotal"] == 17000.0
    assert body["discount"] == 1000.0
    assert body["taxable_amount"] == 16000.0
    assert body["tax"] == 1920.0
    assert body["total"] == 17920.0


def test_calculate_does_not_write_invoice(client, payload):
    client.post("/api/invoices/calculate", json=payload)
    r = client.get("/api/invoices")
    assert r.json() == []


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------
def test_create_invoice(client, payload):
    r = client.post("/api/invoices", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["invoice_number"] == "INV-0001"
    assert body["totals"]["total"] == 17920.0
    assert body["business"]["name"] == "ACME Digital Solutions"
    assert body["customer"]["name"] == "Juan Dela Cruz"


def test_create_invoice_unknown_business_returns_404(client, customer, payload):
    bad = {**payload, "business_id": 999999}
    r = client.post("/api/invoices", json=bad)
    assert r.status_code == 404
    assert r.json()["error"] == "BUSINESS_NOT_FOUND"


def test_create_invoice_unknown_customer_returns_404(client, business, payload):
    bad = {**payload, "customer_id": 999999}
    r = client.post("/api/invoices", json=bad)
    assert r.status_code == 404
    assert r.json()["error"] == "CUSTOMER_NOT_FOUND"


def test_duplicate_create_returns_409(client, payload):
    client.post("/api/invoices", json=payload)
    r = client.post("/api/invoices", json=payload)
    assert r.status_code == 409
    assert r.json()["error"] == "DUPLICATE_INVOICE"


def test_two_invoices_can_share_business_and_customer(client, payload):
    client.post("/api/invoices", json=payload)
    second = {**payload, "invoice_number": "INV-0002"}
    r = client.post("/api/invoices", json=second)
    assert r.status_code == 201
    listing = client.get("/api/invoices").json()
    assert len(listing) == 2
    assert {inv["invoice_number"] for inv in listing} == {"INV-0001", "INV-0002"}


# ---------------------------------------------------------------------------
# Get
# ---------------------------------------------------------------------------
def test_get_invoice(client, payload):
    client.post("/api/invoices", json=payload)
    r = client.get("/api/invoices/INV-0001")
    assert r.status_code == 200
    assert r.json()["invoice_number"] == "INV-0001"


def test_get_nonexistent_returns_404(client):
    r = client.get("/api/invoices/INV-9999")
    assert r.status_code == 404
    assert r.json()["error"] == "INVOICE_NOT_FOUND"


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------
def test_list_invoices(client, payload):
    client.post("/api/invoices", json=payload)
    r = client.get("/api/invoices")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["invoice_number"] == "INV-0001"
    assert body[0]["customer_name"] == "Juan Dela Cruz"


# ---------------------------------------------------------------------------
# Update (PUT)
# ---------------------------------------------------------------------------
def test_update_invoice_recalculates_totals(client, payload):
    client.post("/api/invoices", json=payload)
    updated = {**payload, "items": [
        {"description": "Web Design", "quantity": 2, "unit_price": 15000},
        {"description": "Website Hosting", "quantity": 2, "unit_price": 1000},
    ]}
    r = client.put("/api/invoices/INV-0001", json=updated)
    assert r.status_code == 200
    body = r.json()
    # subtotal = 30000 + 2000 = 32000; discount=1000; taxable=31000; tax=3720; total=34720
    assert body["totals"]["total"] == 34720.0


def test_update_preserves_created_at_and_sets_updated_at(client, payload):
    client.post("/api/invoices", json=payload)
    original = client.get("/api/invoices/INV-0001").json()
    r = client.put("/api/invoices/INV-0001", json=payload)
    assert r.status_code == 200
    updated = r.json()
    assert updated["created_at"] == original["created_at"]
    assert "updated_at" in updated


def test_update_changes_business_reference_without_mutating_shared_row(client, payload):
    client.post("/api/invoices", json=payload)
    other_business = client.post("/api/businesses", json={
        "name": "Other Co",
        "address": "Manila, Philippines",
        "email": "hello@otherco.com",
    }).json()

    updated = {**payload, "business_id": other_business["id"]}
    r = client.put("/api/invoices/INV-0001", json=updated)
    assert r.status_code == 200
    assert r.json()["business"]["id"] == other_business["id"]

    # Original business row must be untouched.
    original_business = client.get(f"/api/businesses/{payload['business_id']}").json()
    assert original_business["name"] == "ACME Digital Solutions"


def test_update_number_mismatch_returns_400(client, payload):
    client.post("/api/invoices", json=payload)
    mismatch = {**payload, "invoice_number": "INV-0002"}
    r = client.put("/api/invoices/INV-0001", json=mismatch)
    assert r.status_code == 400
    assert r.json()["error"] == "INVOICE_NUMBER_MISMATCH"


def test_update_nonexistent_returns_404(client, payload):
    r = client.put("/api/invoices/INV-9999", json={**payload, "invoice_number": "INV-9999"})
    assert r.status_code == 404


def test_update_overwrites_in_place(client, payload):
    client.post("/api/invoices", json=payload)
    client.put("/api/invoices/INV-0001", json=payload)
    listing = client.get("/api/invoices").json()
    assert len(listing) == 1


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------
def test_delete_invoice(client, payload):
    client.post("/api/invoices", json=payload)
    r = client.delete("/api/invoices/INV-0001")
    assert r.status_code == 200
    assert r.json()["message"] == "Invoice deleted successfully"
    r2 = client.get("/api/invoices/INV-0001")
    assert r2.status_code == 404


def test_delete_nonexistent_returns_404(client):
    r = client.delete("/api/invoices/INV-9999")
    assert r.status_code == 404


def test_delete_invoice_does_not_delete_shared_business(client, payload):
    client.post("/api/invoices", json=payload)
    client.delete("/api/invoices/INV-0001")
    r = client.get(f"/api/businesses/{payload['business_id']}")
    assert r.status_code == 200


# ---------------------------------------------------------------------------
# Validation / 422
# ---------------------------------------------------------------------------
def test_validation_error_returns_422(client, payload):
    bad = {**payload, "tax_rate": 5.0}  # > 1
    r = client.post("/api/invoices", json=bad)
    assert r.status_code == 422


def test_validation_error_has_field_detail(client, payload):
    bad = {**payload, "items": []}
    r = client.post("/api/invoices", json=bad)
    assert r.status_code == 422
    # FastAPI 422 body has "detail" list
    assert "detail" in r.json()


def test_create_invoice_accepts_optional_notes_and_payment_method(client):
    payload = {
        **PAYLOAD,
        "notes": "Net 15 days",
        "payment_method": "Bank transfer",
    }
    r = client.post("/api/invoices", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["notes"] == "Net 15 days"
    assert body["payment_method"] == "Bank transfer"


def test_invalid_email_returns_field_specific_validation_error(client):
    bad = {**PAYLOAD, "customer": {"name": "Juan Dela Cruz", "email": "not-an-email"}}
    r = client.post("/api/invoices", json=bad)
    assert r.status_code == 422
    detail = r.json()["detail"]
    assert any("email" in msg.lower() for msg in [item["msg"] for item in detail])


# ---------------------------------------------------------------------------
# Path traversal
# ---------------------------------------------------------------------------
def test_path_traversal_rejected(client, payload):
    bad = {**payload, "invoice_number": "../evil"}
    r = client.post("/api/invoices", json=bad)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# X-Request-ID header
# ---------------------------------------------------------------------------
def test_request_id_header_present(client):
    r = client.get("/api/health")
    assert "x-request-id" in r.headers
