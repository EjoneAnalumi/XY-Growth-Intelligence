# Week 2 Day 9 Sales Workflow Dashboard Evidence

Date: 07-08-2026

Branch: `feature/sales-workflow-dashboard-integration`

## Scope

Day 9 requires:

- Integrate dashboard.
- Integrate scoring.
- Integrate priority logic.
- Integrate tasks.
- Add inactive-opportunity logic.
- Verify that sales workflow updates dashboard accurately.

## Implemented

- Replaced the placeholder frontend dashboard with a live dashboard connected to `GET /dashboard/summary`.
- Added frontend dashboard API mapping and typed dashboard models.
- Added dashboard KPIs for:
  - open pipeline value
  - weighted pipeline value
  - high-priority opportunities
  - open tasks
  - overdue tasks
  - tasks due this week
  - inactive opportunities
- Added priority opportunity cards linking to opportunity detail pages.
- Added stage summary and pipeline health sections.
- Extended backend dashboard response with:
  - `open_tasks`
  - `high_priority_opportunities`
  - `inactive_opportunities`
  - `priority_opportunities`
- Integrated ICP scoring into priority ranking through company `fit_score`.
- Added inactive-opportunity logic for open deals with at least 14 days in stage and no recent activity or open task.

## Priority Logic

Priority score uses deterministic inputs:

- Weighted opportunity value.
- Latest company ICP `fit_score`.
- Overdue or due-this-week task state.
- Inactive-opportunity status.

The score is capped at 100 and returned with a short reason string.

## Verified Workflow

The automated test covers this flow:

1. Create a strong-fit company.
2. Calculate ICP score.
3. Create a high-value opportunity.
4. Create a due-this-week task for that opportunity.
5. Create an inactive open opportunity.
6. Verify dashboard summary shows:
   - one open task
   - one task due this week
   - one inactive opportunity
   - one high-priority opportunity
7. Complete the task.
8. Verify dashboard task counts update.

## Security Notes

- No real customer, prospect, credential, or API key data was added.
- Dashboard endpoint still requires authenticated bearer auth.
- ICP and task write permissions remain enforced by backend role checks.

## Verification

Commands to run:

```powershell
cd backend
python -m pytest
python -m ruff check .

cd ..\frontend
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
```
