"""Application configuration loaded from environment variables."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend/ directory (one level up from app/)
_backend_dir = Path(__file__).parent.parent
load_dotenv(_backend_dir / ".env")

BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))
FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "DEBUG").upper()

# DATA_FILE_DIR is relative to the backend/ directory
_data_dir_env = os.getenv("DATA_FILE_DIR", "data")
DATA_DIR: Path = (_backend_dir / _data_dir_env).resolve()

LOG_DIR: Path = (_backend_dir.parent / "logs").resolve()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/invoice_generator",
)
