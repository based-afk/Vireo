# Vireo — Privacy-First Personal Finance Tracker

A privacy-focused personal finance and cashflow tracking application designed to give users control over their financial data. Combines manual transaction management with a secure bank-statement import workflow, allowing users to inspect and validate extracted transactions before they are persisted. Built with a **React + Vite** frontend, a **FastAPI (Python)** backend, and **PostgreSQL** with **SQLAlchemy ORM**.

---

## Table of Contents

- [About the Project](#about-the-project)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Database & Data Models (ER Diagram)](#database--data-models-er-diagram)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [1. Database Setup](#1-database-setup)
  - [2. Backend Setup (FastAPI)](#2-backend-setup-fastapi)
  - [3. Frontend Setup (React + Vite)](#3-frontend-setup-react--vite)
- [API Reference](#api-reference)
- [Testing & Verification](#testing--verification)
- [Security & Privacy Principles](#security--privacy-principles)

---

## About the Project

**Vireo** is a privacy-focused personal finance and cashflow tracking application designed to give users control over their financial data. It combines manual transaction management with a secure bank-statement import workflow, allowing users to inspect and validate extracted transactions before they are persisted.

Unlike services that require direct banking credentials or rely on third-party financial aggregators, Vireo is designed around explicit user control, transparent data processing, and minimal retention of sensitive information.

The project aims to provide a complete personal finance workflow—from transaction recording and spending analysis to intelligent categorization—while keeping the user in control of imported financial data.

### Core Principles

- **User-Controlled Data:** Transactions are explicitly entered or imported by the user.
- **Privacy by Design:** Sensitive information is processed only when needed, with particular care around statement passwords and unconfirmed imports.
- **Review Before Persistence:** Imported transactions are parsed and presented for inspection before being saved.
- **Transparency:** Malformed or ambiguous records are flagged for review rather than silently accepted.
- **Incremental Intelligence:** Automated categorization is intended to assist users without replacing their ability to correct predictions.

---

## Key Features

### 1. Transaction Management

- Record income and expenses manually.
- Associate transactions with categories and transaction metadata.
- View transactions in a centralized ledger.
- Format monetary values in Indian Rupees (₹).
- Support filtering, sorting and transaction review through a responsive interface.

### 2. PDF Bank Statement Importer

Vireo provides a statement-import workflow designed to extract transaction information from digital PDF bank statements without requiring direct access to the user's bank account.

- **In-Memory Extraction:** Extract text from uploaded PDFs using Python and `pdfplumber`.
- **Password-Protected PDFs:** Detect encrypted documents and request a password through a masked dialog.
- **Retry Without Re-uploading:** Allow users to retry extraction after an incorrect password.
- **Structured Transaction Parsing:** Convert statement text into transaction dates, narrations, withdrawals, deposits and closing balances.
- **Multiline Narration Handling:** Reconstruct descriptions that span multiple lines.
- **Statement Cleanup:** Recognize repeated page headers, footers and statement-summary rows.
- **Validation and Review:** Flag ambiguous or malformed transaction rows for human inspection.
- **Financial Summaries:** Calculate transaction counts, total withdrawals, total deposits and net movement from parsed records.
- **Reconciliation Checks:** Compare parsed transaction totals with corresponding totals printed in the statement when available.
- **Raw Text Diagnostics:** Keep the extracted text available for troubleshooting when structured parsing needs inspection.
- **Scanned PDF Detection:** Identify documents without usable extractable text and indicate when OCR support would be required.

The import workflow is designed to separate extraction and preview from database persistence. Parsed records remain drafts until a future confirmation-and-import workflow is implemented.

### 3. Financial Dashboard

The dashboard is intended to provide a consolidated view of personal cashflow through:

- Total income and expenditure.
- Current-period financial summaries.
- Recent transactions.
- Spending trends over time.
- Category-level expense breakdowns.
- Quick access to transaction management and analytics.

Dashboard figures should ultimately be derived from persisted transaction data rather than static demonstration values.

### 4. Spending Analytics

The analytics module is intended to help users understand where their money goes and how spending changes over time. Planned capabilities include monthly income and expense comparisons, spending trends over configurable periods, category-wise expenditure breakdowns, and cashflow summaries.

### 5. Transaction Categorization

Vireo's longer-term scope includes automated transaction categorization using a combination of deterministic rules and machine learning:

- Merchant and narration-based rules for recognizable transactions.
- A Naive Bayes text-classification baseline for transaction descriptions.
- User confirmation and correction of predicted categories.
- A labelled dataset built from manually confirmed transactions.
- Confidence-based review for uncertain predictions.

Confirmed labels will be treated as the source of truth for training. Unreviewed predictions should not automatically become training labels.

### 6. Privacy and Security

- No requirement to provide banking credentials for statement imports.
- Password-protected PDFs are unlocked through the PDF library's native decryption support.
- Statement passwords are not stored in the database, browser storage, application logs or URLs.
- Uploaded PDF contents are processed in memory during preview.
- Unconfirmed draft transactions are kept separate from persisted ledger records.
- File-size limits and input validation reduce risks associated with uploads.

### 7. Responsive User Interface

- Dark-first interface with a restrained, finance-oriented visual design.
- React components for dashboards, transaction tables, analytics and statement imports.
- Responsive layouts for different screen sizes.
- Currency and date formatting suited to the intended user experience.
- Clear loading, empty, error and review states.

---

## System Architecture

```mermaid
flowchart TD
    subgraph Client ["Client (React + Vite SPA)"]
        UI["Dark UI Shell\n(Dashboard, Transactions, Import, Analytics)"]
        APICall["API Helper (Axios)\nclient/src/api.js"]
        State["React State & In-Memory Cache\n(Zero WebStorage Persistence for Sensitive Data)"]
        UI --> APICall
        APICall <--> State
    end

    subgraph Server ["Backend (FastAPI Python)"]
        CORS["CORS & Error Handlers\n(Sanitized Error Responses)"]
        Routes["API Endpoints\n- /api/health\n- /api/transactions\n- /api/imports/preview"]
        
        subgraph Services ["Core Services"]
            PDFExt["PDF Extraction Service\napp/services/pdf_extractor.py\n(pdfplumber / pdfminer)"]
            Parser["Statement Parser Service\napp/services/statement_parser.py\n(Regex Normalization & Validation)"]
        end
        
        Models["SQLAlchemy ORM & Pydantic Schemas\napp/models.py & app/schemas.py"]
    end

    subgraph Database ["Persistence Layer"]
        Postgres[("PostgreSQL Database\n(moneta)")]
    end

    APICall <-->|"HTTP / JSON (REST)"| CORS
    CORS --> Routes
    Routes -->|"Query / Insert"| Models
    Routes -->|"In-Memory Stream"| PDFExt
    PDFExt -->|"Raw Page Text"| Parser
    Parser -->|"Structured Preview (No DB Write)"| Routes
    Models <-->|"SQLAlchemy Engine"| Postgres
```

---

## Database & Data Models (ER Diagram)

### Persistent Relational Model (PostgreSQL)

```mermaid
erDiagram
    TRANSACTIONS {
        bigserial id PK "Unique identifier"
        varchar title "Transaction description (1-120 chars)"
        numeric amount "Transaction amount (gt 0, max 2 decimals)"
        varchar type "INCOME or EXPENSE"
        varchar category "Category classification (e.g. Food, Bills)"
        date transaction_date "Date transaction took place"
        timestamptz created_at "Timestamp of entry creation"
    }
```

### In-Memory Statement Preview Model (Non-Persistent)

```mermaid
classDiagram
    class PDFPreviewResponse {
        +string filename
        +string status
        +string message
        +int total_pages
        +int total_characters
        +int total_words
        +PDFPagePreview[] pages
        +PDFDiagnostics diagnostics
        +ParsedStatement statement
    }

    class ParsedStatement {
        +bool has_transactions
        +string format_detected
        +StatementSummary summary
        +ParsedTransaction[] transactions
        +string[] unparsed_lines
        +string[] parsing_warnings
    }

    class ParsedTransaction {
        +int row_number
        +string date
        +string original_date
        +string narration
        +string type
        +float amount
        +float withdrawal
        +float deposit
        +float closing_balance
        +string status
        +string[] issues
    }

    class StatementSummary {
        +int total_transactions
        +int valid_count
        +int needs_review_count
        +float total_withdrawals
        +float total_deposits
        +float net_change
        +float statement_total_withdrawals
        +float statement_total_deposits
        +float statement_net_income
        +float statement_closing_balance
    }

    PDFPreviewResponse --> ParsedStatement
    ParsedStatement --> StatementSummary
    ParsedStatement --> ParsedTransaction
```

---

## Tech Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 19, Vite | Modern single-page application and fast HMR dev server |
| **Styling** | Tailwind CSS + Custom CSS | Accessible dark aesthetic with high contrast tokens |
| **Icons** | Lucide React | Lightweight, consistent vector iconography |
| **HTTP Client** | Axios | Frontend request handler |
| **Backend** | FastAPI (Python 3.11+) | Async-ready, auto-documenting REST API framework |
| **Validation** | Pydantic v2 | Strict request and response contract validation |
| **ORM & DB** | SQLAlchemy 2.0, PostgreSQL | Structured database management with parameterized queries |
| **PDF Extraction**| `pdfplumber`, `pdfminer.six`, `pypdf` | In-memory text extraction & standard password decryption |
| **Testing** | `unittest`, `FastAPI TestClient` | Comprehensive test suite for APIs and parsing services |

---

## Repository Structure

```text
Vireo/
├── client/                     # Frontend Single Page Application
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   │   ├── import/         # Statement table and row components
│   │   │   ├── layout/         # Header, sidebar, and navigation shells
│   │   │   ├── transactions/   # Transaction ledger tables and modal dialogs
│   │   │   └── ui/             # Generic empty states and badges
│   │   ├── pages/              # Top-level view routes (Dashboard, Import, etc.)
│   │   ├── utils/              # INR Currency and date formatters
│   │   ├── api.js              # Axios API instance and endpoints
│   │   └── styles.css          # Design system variables and styling rules
│   └── package.json
│
├── server/                     # Backend API & Extraction Engine
│   ├── app/
│   │   ├── services/           # Domain business logic
│   │   │   ├── pdf_extractor.py     # PDF stream extraction and decryption
│   │   │   └── statement_parser.py  # Bank statement text to row parser
│   │   ├── config.py           # Environment variables and limits
│   │   ├── database.py         # SQLAlchemy engine and session dependency
│   │   ├── models.py           # SQLAlchemy database entities
│   │   ├── schemas.py          # Pydantic input/output validation models
│   │   └── main.py             # FastAPI router, CORS, and exception handlers
│   ├── db/
│   │   └── schema.sql          # PostgreSQL DDL schema definition
│   ├── tests/                  # Automated test suites
│   │   ├── test_pdf_import.py       # PDF service and upload integration tests
│   │   └── test_statement_parser.py # Bank statement regex & summary unit tests
│   └── requirements.txt
│
└── README.md
```

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- **Node.js**: `v20.0.0` or higher
- **npm**: `v10.0.0` or higher
- **Python**: `v3.11` or higher
- **PostgreSQL**: `v14` or higher (running locally or accessible via network)

---

### 1. Database Setup

1. Start your PostgreSQL service.
2. Create the `vireo` database:
   ```bash
   psql -U postgres -c "CREATE DATABASE vireo;"
   ```
3. Initialize the database schema:
   ```bash
   psql -U postgres -d vireo -f server/db/schema.sql
   ```

---

### 2. Backend Setup (FastAPI)

1. Navigate to the `server/` directory:
   ```bash
   cd server
   ```

2. Create and activate a Python virtual environment:
   - **Windows**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   # Copy the sample environment file
   copy .env.example .env    # Windows
   cp .env.example .env      # macOS/Linux
   ```
   Open `.env` and verify your PostgreSQL credentials:
   ```env
   DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/vireo
   CLIENT_ORIGIN=http://localhost:5173
   MAX_UPLOAD_SIZE_BYTES=10485760
   ```

5. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - API Root: `http://localhost:8000`
   - Health Check: `http://localhost:8000/api/health`
   - Interactive Swagger Docs: `http://localhost:8000/docs`

---

### 3. Frontend Setup (React + Vite)

1. Open a new terminal and navigate to the `client/` directory:
   ```bash
   cd client
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open `http://localhost:5173` in your browser.

---

## API Reference

### Health Check
- **`GET /api/health`**
  - **Response `200`**: `{"status": "ok", "database": "connected"}`

### Transactions
- **`GET /api/transactions`**
  - Lists all stored transactions ordered by date descending.
  - **Response `200`**: `{"transactions": [...]}`

- **`POST /api/transactions`**
  - Creates a new financial record.
  - **Payload**:
    ```json
    {
      "title": "Grocery Shopping",
      "amount": 2450.50,
      "type": "EXPENSE",
      "category": "Groceries",
      "date": "2026-10-14"
    }
    ```
  - **Response `201`**: `{"message": "Transaction created.", "transaction": {...}}`

### Bank Statement Preview (In-Memory)
- **`POST /api/imports/preview`**
  - Uploads a PDF bank statement for inspection and parsing without persisting to database.
  - **Form Data**:
    - `file`: PDF file (`.pdf`, max 10 MB).
    - `password` *(optional)*: String password for encrypted PDFs.
  - **Outcomes**:
    - `200 OK` (Success): Returns page diagnostics, parsed transactions list, and financial summary totals.
    - `200 OK` (`password_required`): Indicates document is encrypted and requires a password.
    - `200 OK` (`ocr_needed`): Indicates document has no digital text layer and requires OCR.
    - `400 Bad Request` (`incorrect_password`): Supplied password failed decryption.
    - `400 Bad Request` (`invalid_pdf`): Corrupt or non-PDF binary payload.

---

## Testing & Verification

### Running Backend Tests
The backend includes unit and integration tests covering PDF decryption, text extraction, edge cases, summary row exclusions, and API contracts.

```bash
cd server
.venv\Scripts\python -m unittest discover -s tests
```
*(Runs 29 test cases covering ordinary PDFs, encrypted PDFs, multiline statement rows, and summary exclusion).*

### Running Frontend Production Build
Validate that the React frontend builds without errors:

```bash
cd client
npm run build
```

---

## Security & Privacy Principles

1. **In-Memory Statement Execution**: Statement PDFs are processed in an in-memory byte buffer (`io.BytesIO`) and closed immediately after preview generation.
2. **Ephemeral Passwords**: Document passwords are submitted via multipart POST body, never placed in query strings, never logged to stdout, and never stored in `localStorage` or cookies.
3. **Draft Separation**: Imported transactions remain in frontend state as a preview until explicitly confirmed by the user.
4. **Sanitized Error Reporting**: Database connection strings, stack traces, and internal PDF parser exceptions are intercepted and replaced with user-friendly error codes.

