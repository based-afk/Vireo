# Moneta (Vireo) — Personal Finance Management

A modern, privacy-focused, dark-first personal finance application designed for granular transaction tracking and intelligent bank statement ingestion. Built with a **React + Vite** frontend, a high-performance **FastAPI (Python)** backend, and **PostgreSQL** with **SQLAlchemy ORM**.

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

**Moneta** simplifies personal cashflow tracking while upholding strict privacy standards. Unlike services that require direct banking credentials or sync unvetted third-party cloud aggregators, Moneta provides a secure, client-controlled workflow:

1. **Explicit Tracking**: Log and categorize daily income and expense transactions.
2. **In-Memory Statement Import**: Upload standard digital or password-protected PDF bank statements to preview extracted transactions and verification summaries **before** anything is saved to the database.
3. **Zero Leaks**: Encrypted PDFs are unlocked on-the-fly in memory. Passwords and unconfirmed draft transactions are never persisted, cached, or written to disk.

---

## Key Features

- **Dark-First Premium UI**: Sleek, responsive interface built with Tailwind CSS, custom dark tokens, and micro-interactions.
- **Transaction Ledger**: Fast creation and listing of income and expense records with category pills and currency formatting (₹ INR).
- **PDF Bank Statement Importer**:
  - Extracts tabular transaction rows (`Txn Date`, `Narration`, `Withdrawals`, `Deposits`, `Closing Balance`).
  - Merges multiline narrations across line wraps seamlessly.
  - Excludes page headers, footers, and statement-summary total rows from transaction counts.
  - Flags ambiguous or malformed rows for human review rather than silently dropping them.
- **Password-Protected PDF Support**:
  - Detects encrypted PDFs and prompts with a secure, masked password modal.
  - In-place retry for incorrect passwords without requiring file re-upload.
  - Zero retention: passwords are immediately wiped from memory after processing.
- **Scanned Document Detection**: Identifies image-only or scanned statements that require OCR (optical character recognition) and provides diagnostic feedback.

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
2. Create the `moneta` database:
   ```bash
   psql -U postgres -c "CREATE DATABASE moneta;"
   ```
3. Initialize the database schema:
   ```bash
   psql -U postgres -d moneta -f server/db/schema.sql
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
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moneta
   ALLOWED_ORIGINS=http://localhost:5173
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
