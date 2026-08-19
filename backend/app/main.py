"""FastAPI application entry point.

Responsibilities:
  - Initialise logging (first thing, before any other import logs)
  - Configure CORS restricted to FRONTEND_URL
  - Register request-ID middleware
  - Register domain exception handlers
  - Mount the invoice router
"""
import logging
import secrets
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import FRONTEND_URL
from app.utils.logging_config import setup_logging
from app.utils.errors import (
    BusinessNotFoundError,
    CustomerNotFoundError,
    DatabaseError,
    DuplicateInvoiceError,
    InvoiceNotFoundError,
)

# Must be called before any logger is obtained
setup_logging()

from app.api.businesses import router as businesses_router  # noqa: E402 — after logging setup
from app.api.customers import router as customers_router  # noqa: E402 — after logging setup
from app.api.invoices import router as invoices_router  # noqa: E402 — after logging setup

logger = logging.getLogger(__name__)

app = FastAPI(title="Invoice Generator API", version="1.0.0")

# ---------------------------------------------------------------------------
# CORS — only the configured frontend origin is allowed
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# ---------------------------------------------------------------------------
# Request-ID middleware
# Generates an 8-char hex ID per request, attaches it to request.state,
# prefixes log lines, and returns it as a response header.
# ---------------------------------------------------------------------------
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = secrets.token_hex(4)  # 8 hex chars
    request.state.request_id = request_id

    start = time.perf_counter()
    response = await call_next(request)
    elapsed = int((time.perf_counter() - start) * 1000)

    response.headers["X-Request-ID"] = request_id
    logger.debug(
        "[req %s] %s %s → %d (%dms)",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------
def _error_body(code: str, message: str, request_id: str) -> dict:
    return {"error": code, "message": message, "request_id": request_id}


@app.exception_handler(InvoiceNotFoundError)
async def not_found_handler(request: Request, exc: InvoiceNotFoundError):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.info("[req %s] InvoiceNotFoundError: %s", req_id, exc.message)
    return JSONResponse(
        status_code=404,
        content=_error_body("INVOICE_NOT_FOUND", exc.message, req_id),
    )


@app.exception_handler(BusinessNotFoundError)
async def business_not_found_handler(request: Request, exc: BusinessNotFoundError):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.info("[req %s] BusinessNotFoundError: %s", req_id, exc.message)
    return JSONResponse(
        status_code=404,
        content=_error_body("BUSINESS_NOT_FOUND", exc.message, req_id),
    )


@app.exception_handler(CustomerNotFoundError)
async def customer_not_found_handler(request: Request, exc: CustomerNotFoundError):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.info("[req %s] CustomerNotFoundError: %s", req_id, exc.message)
    return JSONResponse(
        status_code=404,
        content=_error_body("CUSTOMER_NOT_FOUND", exc.message, req_id),
    )


@app.exception_handler(DuplicateInvoiceError)
async def duplicate_handler(request: Request, exc: DuplicateInvoiceError):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.info("[req %s] DuplicateInvoiceError: %s", req_id, exc.message)
    return JSONResponse(
        status_code=409,
        content=_error_body("DUPLICATE_INVOICE", exc.message, req_id),
    )


@app.exception_handler(DatabaseError)
async def database_error_handler(request: Request, exc: DatabaseError):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error("[req %s] DatabaseError: %s", req_id, exc.message, exc_info=True)
    return JSONResponse(
        status_code=500,
        content=_error_body("DATABASE_ERROR", exc.message, req_id),
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "unknown")
    logger.error("[req %s] Unhandled exception: %s", req_id, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content=_error_body("INTERNAL_ERROR", "An unexpected error occurred.", req_id),
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(invoices_router)
app.include_router(businesses_router)
app.include_router(customers_router)

logger.info("Invoice Generator API started. CORS origin: %s", FRONTEND_URL)
