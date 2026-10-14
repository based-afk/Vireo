import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator

ALLOWED_CATEGORIES = {
    'Food & Dining', 'Shopping', 'Transport', 'Bills & Utilities',
    'Entertainment', 'Healthcare', 'Groceries', 'Education',
    'Transfers', 'Income', 'Others'
}

TransactionType = Literal["INCOME", "EXPENSE"]


class TransactionCreate(BaseModel):
    title: str = Field(..., max_length=120)
    amount: Decimal = Field(..., gt=0)
    type: TransactionType
    category: str
    date: datetime.date

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title is required.")
        if len(trimmed) > 120:
            raise ValueError("Title must be 120 characters or fewer.")
        return trimmed

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        # Check max 2 decimal places
        if v.as_tuple().exponent < -2:
            raise ValueError("Amount can have at most two decimal places.")
        return v

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if v not in ALLOWED_CATEGORIES:
            raise ValueError("Choose a valid category.")
        return v


class TransactionRead(BaseModel):
    id: int
    title: str
    amount: float
    type: str
    category: str
    date: datetime.date = Field(validation_alias="transaction_date")
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TransactionCreateResponse(BaseModel):
    message: str = "Transaction created."
    transaction: TransactionRead


class TransactionListResponse(BaseModel):
    transactions: list[TransactionRead]


class HealthResponse(BaseModel):
    status: str
    database: str


class PDFPagePreviewSchema(BaseModel):
    page_number: int
    character_count: int
    word_count: int
    text: str
    has_images: bool = False
    error: str | None = None


class PDFDiagnosticsSchema(BaseModel):
    has_extractable_text: bool
    ocr_likely_required: bool
    is_encrypted: bool
    page_count: int
    image_count: int = 0


class ParsedTransactionSchema(BaseModel):
    row_number: int
    date: str | None = None
    original_date: str | None = None
    narration: str
    type: Literal["EXPENSE", "INCOME", "UNKNOWN"]
    amount: float = 0.0
    withdrawal: float = 0.0
    deposit: float = 0.0
    closing_balance: float | None = None
    status: Literal["valid", "needs_review"]
    issues: list[str] = Field(default_factory=list)


class StatementSummarySchema(BaseModel):
    total_transactions: int = 0
    valid_count: int = 0
    needs_review_count: int = 0
    total_withdrawals: float = 0.0
    total_deposits: float = 0.0
    net_change: float = 0.0
    statement_total_withdrawals: float | None = None
    statement_total_deposits: float | None = None
    statement_net_income: float | None = None
    statement_closing_balance: float | None = None


class ParsedStatementSchema(BaseModel):
    has_transactions: bool = False
    format_detected: str = "Unknown"
    summary: StatementSummarySchema
    transactions: list[ParsedTransactionSchema] = Field(default_factory=list)
    unparsed_lines: list[str] = Field(default_factory=list)
    parsing_warnings: list[str] = Field(default_factory=list)


class PDFPreviewResponse(BaseModel):
    filename: str
    status: Literal["success", "ocr_needed", "empty", "password_required"]
    message: str
    total_pages: int
    total_characters: int
    total_words: int
    pages: list[PDFPagePreviewSchema]
    diagnostics: PDFDiagnosticsSchema
    statement: ParsedStatementSchema | None = None

