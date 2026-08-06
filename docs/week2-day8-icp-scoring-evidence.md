# Week 2 Day 8 ICP Scoring Evidence

Date: 06-08-2026

Branch: `feature/icp-scoring-engine`

## Scope

Day 8 Intern 1 requires:

- ICP rules.
- Deterministic scoring engine.
- Stored score explanations.
- Tests proving the same inputs always produce the same documented score.

## Implemented

- Added deterministic ICP scoring engine in `backend/app/scoring/icp.py`.
- Added ICP response schemas in `backend/app/schemas/icp.py`.
- Added `POST /companies/{company_id}/calculate-icp`.
- Extended company schemas with fields already present in the database contract:
  - `annual_revenue_usd`
  - `cloud_usage`
  - `regulatory_context`
  - `lifecycle_stage`
  - `fit_score`
- Added in-memory storage for ICP score results and explanations.
- Updated the company `fit_score` after calculation.
- Added Supabase migration for:
  - `icp_rules`
  - `icp_score_results`
  - indexes
  - RLS policies
  - synthetic rule definitions

## Scoring Rules

The score is out of 100:

- Industry fit: 25 points.
- Company size: 20 points.
- Revenue fit: 15 points.
- Regulatory context: 15 points.
- Cloud usage: 10 points.
- Geography: 5 points.
- Lead source: 5 points.
- Lifecycle signal: 5 points.

Each rule returns:

- rule id
- label
- points awarded
- maximum points
- human-readable explanation

## Verified Known Score

The automated test uses this known strong-fit input:

- Financial Services industry.
- 650 employees.
- 75000000 annual revenue.
- United States headquarters.
- Azure and AWS cloud usage.
- PCI DSS and SOX regulatory context.
- Partner referral lead source.
- Qualified lifecycle.

Expected result:

- `score`: 100
- `max_score`: 100
- `tier`: `strong_fit`
- 8 stored rule explanations.
- company `fit_score` updated to 100.

## Security Notes

- ICP calculation requires an authenticated writer role.
- Read-only users cannot calculate ICP scores.
- No real company, customer, prospect, or credential data was added.
- Migration uses RLS for rule reads and score result inserts.

## Verification

Commands to run:

```powershell
cd backend
python -m pytest
python -m ruff check .
```

Expected result:

- All backend tests pass.
- Ruff reports no lint errors.

## Remaining TODO

- Replace in-memory storage with Supabase-backed runtime persistence.
- Add Supabase RLS allow/deny tests after a test Supabase project is available.
- Expose latest ICP score retrieval only when the frontend needs it.
