"""Invoice API routes — validation, delegation to service, response shaping.

Zero business logic. Zero direct database access.
"""
import logging
import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.invoice import InvoiceCreate
from app.repositories import invoice_repository
from app.services import invoice_service

router = APIRouter(prefix="/api")
logger = logging.getLogger(__name__)


@router.get("/health")
async def health(request: Request, db: Session = Depends(get_db)):
    req_id = request.state.request_id
    logger.info("[req %s] GET /api/health started", req_id)
    invoices = invoice_repository.list_all(db)
    result = {
        "status": "ok",
        "data_dir": "postgresql",
        "invoice_count": len(invoices),
    }
    logger.info("[req %s] GET /api/health completed", req_id)
    return result


@router.get("/invoices")
async def list_invoices(request: Request, db: Session = Depends(get_db)):
    req_id = request.state.request_id
    logger.info("[req %s] GET /api/invoices started", req_id)
    all_inv = invoice_service.get_all_invoices(db)
    summaries = [
        {
            "invoice_number": inv["invoice_number"],
            "customer_name": inv["customer"].name,
            "total": inv["totals"]["total"],
            "created_at": inv["created_at"],
        }
        for inv in all_inv
    ]
    logger.info("[req %s] GET /api/invoices completed — %d records", req_id, len(summaries))
    return summaries


@router.get("/invoices/{invoice_number}")
async def get_invoice(invoice_number: str, request: Request, db: Session = Depends(get_db)):
    req_id = request.state.request_id
    logger.info("[req %s] GET /api/invoices/%s started", req_id, invoice_number)
    invoice = invoice_service.get_invoice(db, invoice_number)
    logger.info("[req %s] GET /api/invoices/%s completed", req_id, invoice_number)
    return invoice


@router.post("/invoices/calculate")
async def calculate_invoice(data: InvoiceCreate, request: Request):
    req_id = request.state.request_id
    logger.info("[req %s] POST /api/invoices/calculate started", req_id)
    logger.debug("[req %s] Invoice number: %s", req_id, data.invoice_number)
    logger.debug("[req %s] Item count: %d", req_id, len(data.items))
    totals = invoice_service.calculate(data)
    logger.info("[req %s] POST /api/invoices/calculate completed — total=%s", req_id, totals["total"])
    return totals


@router.post("/invoices", status_code=201)
async def create_invoice(data: InvoiceCreate, request: Request, db: Session = Depends(get_db)):
    req_id = request.state.request_id
    start = time.perf_counter()
    logger.info("[req %s] POST /api/invoices started", req_id)
    logger.debug("[req %s] Invoice number: %s", req_id, data.invoice_number)
    logger.debug("[req %s] Item count: %d", req_id, len(data.items))
    for idx, item in enumerate(data.items):
        logger.debug(
            "[req %s] Item %d: qty=%s unit_price=%s",
            req_id, idx, item.quantity, item.unit_price,
        )
    invoice = invoice_service.create_invoice(db, data)
    elapsed = int((time.perf_counter() - start) * 1000)
    logger.info("[req %s] POST /api/invoices completed in %dms status=201", req_id, elapsed)
    return invoice


@router.put("/invoices/{invoice_number}")
async def update_invoice(invoice_number: str, data: InvoiceCreate, request: Request, db: Session = Depends(get_db)):
    req_id = request.state.request_id
    start = time.perf_counter()
    logger.info("[req %s] PUT /api/invoices/%s started", req_id, invoice_number)

    if data.invoice_number != invoice_number:
        logger.info(
            "[req %s] PUT rejected — path %s != body %s",
            req_id, invoice_number, data.invoice_number,
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "INVOICE_NUMBER_MISMATCH",
                "message": (
                    f"Invoice number in the URL ({invoice_number}) does not match "
                    f"the body ({data.invoice_number}). "
                    "Invoice numbers are immutable — delete and recreate to renumber."
                ),
                "request_id": req_id,
            },
        )

    logger.debug("[req %s] Item count: %d", req_id, len(data.items))
    for idx, item in enumerate(data.items):
        logger.debug(
            "[req %s] Item %d: qty=%s unit_price=%s",
            req_id, idx, item.quantity, item.unit_price,
        )
    invoice = invoice_service.update_invoice(db, invoice_number, data)
    elapsed = int((time.perf_counter() - start) * 1000)
    logger.info("[req %s] PUT /api/invoices/%s completed in %dms status=200", req_id, invoice_number, elapsed)
    return invoice


@router.delete("/invoices/{invoice_number}")
async def delete_invoice(invoice_number: str, request: Request, db: Session = Depends(get_db)):
    req_id = request.state.request_id
    logger.info("[req %s] DELETE /api/invoices/%s started", req_id, invoice_number)
    invoice_service.delete_invoice(db, invoice_number)
    logger.info("[req %s] DELETE /api/invoices/%s completed", req_id, invoice_number)
    return {"message": "Invoice deleted successfully"}
