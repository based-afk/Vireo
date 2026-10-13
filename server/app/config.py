import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from server directory or current working directory
env_path = Path(__file__).resolve().parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "127.0.0.1")
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(10 * 1024 * 1024)))  # 10 MB default

RAW_DATABASE_URL = os.getenv("DATABASE_URL", "")
# Normalize postgresql:// to postgresql+psycopg:// for SQLAlchemy 2.0 + psycopg 3
if RAW_DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = RAW_DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
elif RAW_DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = RAW_DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
else:
    DATABASE_URL = RAW_DATABASE_URL

CLIENT_ORIGIN = os.getenv("CLIENT_ORIGIN", "http://localhost:5173")

# Support comma-separated origins if specified
ALLOWED_ORIGINS = [origin.strip() for origin in CLIENT_ORIGIN.split(",") if origin.strip()]
if not ALLOWED_ORIGINS:
    ALLOWED_ORIGINS = ["http://localhost:5173"]
