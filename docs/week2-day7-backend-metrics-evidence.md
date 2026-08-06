# Week 2 Day 7 Backend Metrics Evidence

Date: 05-08-2026

Branch: `feature/pipeline-dashboard-metrics`

## Scope

Day 7 Intern 1 requires:

- Weighted value metrics.
- Stage duration tracking.
- Dashboard summaries.
- Seed dataset expansion.
- Verified metrics from known values.

## Implemented

- Added `GET /dashboard/summary`.
- Added dashboard response schemas.
- Added stage duration fields on opportunity responses:
  - `current_stage_entered_at`
  - `days_in_current_stage`
- Kept opportunity weighted value recalculation in the backend repository.
- Added dashboard totals for:
  - total opportunities
  - open opportunities
  - won opportunities
  - lost opportunities
  - open pipeline value
  - weighted open pipeline value
  - overdue tasks
  - tasks due this week
  - activity count
  - average days in current stage
  - per-stage opportunity/value summaries
- Expanded synthetic seed data with:
  - 20 opportunities
  - 40 activities
  - 25 tasks
  - fixed pipeline stage IDs for reliable relationships

## Verified Known Metrics

The automated dashboard test creates known values:

- Open deal: 100000 at 50 percent = 50000 weighted.
- Proposal deal: 40000 at 75 percent = 30000 weighted.
- Won deal: excluded from open pipeline.
- Lost deal: excluded from open pipeline.

Expected dashboard output:

- `total_opportunities`: 4
- `open_opportunities`: 2
- `won_opportunities`: 1
- `lost_opportunities`: 1
- `pipeline_value_usd`: 140000
- `weighted_pipeline_value_usd`: 80000
- `overdue_tasks`: 1
- `due_this_week_tasks`: 1
- `activities_count`: 2

## Security Notes

- Dashboard metrics require authenticated bearer auth.
- No real customer, prospect, or credential data was added.
- Seed values use `.example` domains and synthetic names only.

## Verification

To run after checkout:

```powershell
cd backend
python -m pytest
python -m ruff check .
```
