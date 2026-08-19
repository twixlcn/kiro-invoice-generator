"""Configures application-wide logging.

Call setup_logging() exactly once from main.py before the app starts.

Two file handlers:
  - logs/application.log  DEBUG+  all messages
  - logs/error.log        ERROR+  with tracebacks

One stream handler:
  - console               INFO+   readable during the workshop
"""
import logging
import logging.handlers
from pathlib import Path

from app.config import LOG_DIR, LOG_LEVEL

LOG_FORMAT = "%(asctime)s %(levelname)-7s [%(name)s] %(message)s"


def setup_logging() -> None:
    """Create log directory, attach handlers to the root logger."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)  # handlers filter individually

    # Avoid adding duplicate handlers when uvicorn --reload re-imports
    if root.handlers:
        return

    formatter = logging.Formatter(LOG_FORMAT)

    # --- application.log (DEBUG+) ---
    app_handler = logging.FileHandler(LOG_DIR / "application.log", encoding="utf-8")
    app_handler.setLevel(logging.DEBUG)
    app_handler.setFormatter(formatter)

    # --- error.log (ERROR+) ---
    err_handler = logging.FileHandler(LOG_DIR / "error.log", encoding="utf-8")
    err_handler.setLevel(logging.ERROR)
    err_handler.setFormatter(formatter)

    # --- console (INFO+) ---
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    console_handler.setFormatter(formatter)

    root.addHandler(app_handler)
    root.addHandler(err_handler)
    root.addHandler(console_handler)

    logging.getLogger("uvicorn.access").propagate = False
