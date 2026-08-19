"""Domain exception hierarchy.

All exceptions carry a human-readable message.
HTTP status mapping lives in main.py exception handlers.
"""


class InvoiceError(Exception):
    """Base class for all invoice-domain errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvoiceNotFoundError(InvoiceError):
    """Raised when an invoice file does not exist."""


class DuplicateInvoiceError(InvoiceError):
    """Raised when an invoice with the same number already exists."""


class BusinessNotFoundError(InvoiceError):
    """Raised when a business does not exist."""


class CustomerNotFoundError(InvoiceError):
    """Raised when a customer does not exist."""


class DatabaseError(InvoiceError):
    """Raised on database failures.

    Never swallowed — write/read failures must be visible.
    """
