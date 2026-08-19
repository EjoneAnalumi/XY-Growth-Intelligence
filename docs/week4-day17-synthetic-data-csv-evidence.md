# Week 4 Day 17 Synthetic Data and CSV Evidence

Date: 19-08-2026  
Branch: `feature/day17-synthetic-data-csv`  
Scope: Intern 1 only — 30-company synthetic dataset, company CSV import/export, and reseed review.

## Implemented

- Added `sample-data/companies.csv` with 30 fictional companies using reserved `.example` domains.
- Added protected `POST /companies/import` and `GET /companies/export` endpoints.
- CSV import validates the complete file before records are created; Read Only users are denied writes.
- Existing `database/seed/seed.sql` remains the clean-reseed source and already provisions 30 companies and 50 contacts.

## Security

Only synthetic company data is included. Import is limited to backend writer roles; exported data requires authentication.

## Verification

From `backend/`:

```text
python -m pytest tests/test_company_csv.py
3 passed

python -m ruff check .
All checks passed.
```

## Remaining TODO

`docker compose ps` could not access the local Docker daemon in this environment, so `supabase db reset` could not be executed here. Run it on a machine with Docker/Supabase available, then import `sample-data/companies.csv` and verify the exported file in a spreadsheet.
