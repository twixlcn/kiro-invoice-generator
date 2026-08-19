# Invoice Generator

A workshop app for debugging and failure analysis. Ships working — facilitators inject bugs for participants to find.

## SETUP THE APPLICATION

**Database**

Requires a local PostgreSQL server (developed against v17).
```bash
psql -U postgres -c "CREATE DATABASE invoice_generator;"
```

**Backend**
```bash
cd backend
#Create your virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate   |  macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# Set in backend/.env:
#   DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/invoice_generator

alembic upgrade head          # applies the schema to invoice_generator
uvicorn app.main:app --reload 
```
API: http://localhost:8000  
Docs: http://localhost:8000/docs

**Frontend**
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173

**Tests**
```bash
cd backend
pytest -v
```

## The Trace

```
Button click → invoiceApi.js → FastAPI route → Pydantic model
→ invoice_service → calculator → invoice_repository → PostgreSQL
→ response → InvoicePreview
```

Each hop is logged with a `request_id`. Copy the ID from the browser Network tab, then:
```bash
grep "9f2a1c8b" logs/application.log
```

## Log Files

| File | Level | Contents |
|---|---|---|
| `logs/application.log` | DEBUG | Everything |
| `logs/error.log` | ERROR | Errors with tracebacks |
| console | INFO | Readable during workshop |

> Customer name and email appear in DEBUG lines only.

## Database

PostgreSQL via SQLAlchemy 2.x, migrated with Alembic. Four tables: `businesses`, `customers`, `invoices`, `invoice_items`.

Businesses and customers are **reusable entities** — an invoice references one of each via `business_id`/`customer_id`. Editing an invoice's reference only changes which row it points to; it never mutates the shared business/customer row. Edit those through `PUT /api/businesses/{id}` / `PUT /api/customers/{id}` instead.

The 3 invoices that used to live in `backend/data/*.json` were migrated with `backend/scripts/migrate_json_to_db.py` (one-time, idempotent — safe to rerun; reuses a matching business/customer row instead of duplicating it).

## CI

`.github/workflows/ci.yml` runs on every push and pull request — no deployment yet:
- **backend** — `pytest -v` (pure-logic tests, no database)
- **frontend** — `npm ci` + `vite build`

## Reference Calculation

```
Web Design        1 × ₱15,000  = ₱15,000
Website Hosting   2 × ₱1,000   =  ₱2,000
Subtotal                         ₱17,000
Discount                          ₱1,000
Taxable                          ₱16,000
Tax (12%)                         ₱1,920
TOTAL                            ₱17,920
```
