# Week 4 Day 17 Synthetic Data and CSV Evidence

Date: 19-08-2026
Branch: `feature/day17-synthetic-data-csv`
Scope: Intern 1 only — 30-company synthetic dataset, company CSV import/export, and reseed review.

## Implemented

- Added `sample-data/companies.csv` with 30 fictional companies using reserved `.example` domains.
- Added protected `POST /companies/import` and `GET /companies/export` endpoints.
- CSV import validates the complete file before records are created; Read Only users are denied writes.
- Existing `database/seed/seed.sql` remains the clean-reseed source and already provisions 30 companies and 50 contacts.

## CSV contract

- Encoding: UTF-8 input (UTF-8 BOM accepted); export is UTF-8 with BOM for spreadsheet compatibility.
- Headers: `name` is required. Every supplied header must be one of the canonical export headers, and duplicate headers are rejected.
- Lists: `cloud_usage`, `regulatory_context`, and `tags` are pipe-delimited. Empty cells become null for optional scalar fields and empty lists for list fields.
- Dates: `last_activity_at` and `next_action_due_at` accept ISO 8601 timestamps and export in ISO 8601 format.
- Duplicate policy: reject the entire import with HTTP 409 if a name or domain already exists; duplicate rows in one file are rejected with HTTP 422.
- Validation errors return only row number, field, and stable error code; submitted cell contents are not reflected.

## Security

Only synthetic company data is included. Import is limited to backend writer roles; exported data requires authentication.

## Verification

From `backend/`:

```text
python -m pytest tests/test_company_csv.py
7 passed

python -m ruff check .
All checks passed.
```

Local Supabase verification completed with `supabase db reset`: all migrations applied, the seed
produced 30 active companies, and the RLS permission suite passed. A separate local-only
acceptance run truncated the disposable company test state, imported `sample-data/companies.csv`
with HTTP 201 and `created: 30`, confirmed 30 active database rows, and exported a UTF-8 BOM CSV
that parsed successfully with 30 rows. Re-importing the same file returned HTTP 409 with the count
unchanged at 30. A final `supabase db reset` restored the normal seeded 30-company baseline.
