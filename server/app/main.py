import logging
from fastapi import FastAPI, Depends, status, Request, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.orm import Session

from .config import ALLOWED_ORIGINS, MAX_UPLOAD_SIZE_BYTES
from .database import get_db, check_db_connection
from .models import Transaction
from .schemas import (
    TransactionCreate,
    TransactionCreateResponse,
    TransactionListResponse,
    TransactionRead,
    HealthResponse,
    PDFPreviewResponse,
)
from .services.pdf_extractor import (
    extract_pdf_preview,
    InvalidPDFError,
    EncryptedPDFError,
    EmptyPDFError,
)


logger = logging.getLogger("moneta")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Moneta API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    fields = {}
    first_error_msg = "Validation failed."
    for err in exc.errors():
        loc = err.get("loc", [])
        field_name = str(loc[-1]) if loc else "general"
        msg = err.get("msg", "Invalid value.")
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        fields[field_name] = msg
        if first_error_msg == "Validation failed.":
            first_error_msg = msg

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": first_error_msg,
            "fields": fields,
            "detail": exc.errors(),
        },
    )


@app.get("/api/health", response_model=HealthResponse)
def health_check():
    is_healthy = check_db_connection()
    if is_healthy:
        return {"status": "ok", "database": "connected"}
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "error", "database": "unavailable"},
    )


@app.get("/api/transactions", response_model=TransactionListResponse)
def get_transactions(db: Session = Depends(get_db)):
    try:
        rows = (
            db.query(Transaction)
            .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
            .all()
        )
        return {"transactions": rows}
    except Exception as e:
        logger.error(f"Failed to fetch transactions: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Could not fetch transactions."},
        )


@app.post(
    "/api/transactions",
    response_model=TransactionCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    try:
        new_transaction = Transaction(
            title=payload.title,
            amount=payload.amount,
            type=payload.type,
            category=payload.category,
            transaction_date=payload.date,
        )
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return {
            "message": "Transaction created.",
            "transaction": new_transaction,
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create transaction: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Could not create transaction."},
        )


@app.post("/api/imports/preview", response_model=PDFPreviewResponse)
async def preview_pdf_import(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Uploaded file must be a PDF document (.pdf)."},
        )

    try:
        chunks = []
        total_read = 0
        chunk_size = 1024 * 512  # 512 KB chunks

        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            total_read += len(chunk)
            if total_read > MAX_UPLOAD_SIZE_BYTES:
                max_mb = MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={"error": f"File size exceeds the maximum limit of {max_mb} MB."},
                )
            chunks.append(chunk)

        file_bytes = b"".join(chunks)

        if len(file_bytes) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Uploaded file is empty (0 bytes)."},
            )

        result = extract_pdf_preview(file_bytes, filename=file.filename)
        return result
    except EmptyPDFError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )
    except EncryptedPDFError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )
    except InvalidPDFError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": str(e)},
        )
    except Exception as e:
        logger.error(f"Unexpected error processing PDF import: {type(e).__name__}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "An unexpected error occurred while processing the PDF."},
        )
    finally:
        await file.close()

