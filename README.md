# Moneta — Personal Finance

Dark-first personal finance app using React + Vite + Tailwind CSS, FastAPI (Python), SQLAlchemy, and PostgreSQL.

## Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL 14+
- npm

## Setup

### 1. Database
Create a database:
```sql
CREATE DATABASE moneta;
```
Run the schema:
```bash
psql -d moneta -f server/db/schema.sql
```

### 2. Backend (FastAPI)
```bash
cd server
copy .env.example .env    # Windows (or: cp .env.example .env)
# Configure DATABASE_URL in .env
python -m venv .venv
.venv\Scripts\activate   # Windows (or: source .venv/bin/activate on Unix)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
The API runs at `http://localhost:8000`. Check `GET /api/health`.
API documentation is automatically available at `http://localhost:8000/docs`.

### 3. Frontend
In a second terminal:
```bash
cd client
npm install
npm run dev
```
Open the Vite URL shown in the terminal (default: `http://localhost:5173`).

## First vertical slice
`POST /api/transactions` validates input via Pydantic, inserts a transaction into PostgreSQL using SQLAlchemy ORM, and returns the persisted row. The frontend's Add Transaction dialog calls this endpoint.

## Example request
```bash
curl -X POST http://localhost:8000/api/transactions \
  -H "Content-Type: application/json" \
  -d '{"title":"Lunch","amount":250,"type":"EXPENSE","category":"Food & Dining","date":"2026-10-13"}'
```

## Statement Import (Phase 1)
`POST /api/imports/preview` accepts a multipart PDF file (`file`), extracts text page-by-page using `pdfplumber`, detects image-only/scanned documents where OCR would be required, and returns extraction diagnostics without saving any file or writing to the database.

Example upload preview:
```bash
curl -X POST http://localhost:8000/api/imports/preview \
  -F "file=@statement.pdf"
```

## Current scope
- Shared dark UI shell with Dashboard, Transactions, Import, Analytics, and Settings routes
- Dashboard and Analytics are illustrative UI previews; values are mock data until read endpoints are implemented
- Fully implemented transaction-create and transaction-list endpoints
- Phase 1 bank statement PDF upload and preview extraction (no database writes, OCR indicator)
- No authentication or SMS ingestion yet
