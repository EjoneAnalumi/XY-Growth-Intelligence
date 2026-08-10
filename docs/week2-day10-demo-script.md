# Week 2 Day 10 Demo Script

Date: 2026-08-10

Scope: Week 2 sales workflow gate only.

## Prerequisites

- Backend terminal running FastAPI.
- Frontend terminal running Next.js.
- Synthetic `.example` company/contact data only.
- No real secrets or customer/prospect data.

## Commands

Backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd frontend
npm.cmd run dev
```

Open:

```text
http://localhost:3000/login
```

## Demo Flow

1. Sign in with the local Business Development demo role.
2. Create a fictional company:

```text
Name: Day Ten Finance
Domain: day-ten-finance.example
Industry: Financial Services
Country: United States
```

3. Create a contact linked to the company:

```text
First name: Rina
Last name: Cole
Email: rina.cole@day-ten-finance.example
Decision category: champion
```

4. Calculate the ICP score and show the strong-fit result with rule contributions.
5. Create an opportunity:

```text
Name: Week 2 Regression Managed SOC Pilot
Service: Managed SOC
Value USD: 100000
Probability: 50
```

6. Confirm weighted value is `50000`.
7. Open the opportunity detail page and confirm stage duration fields are visible.
8. Move the opportunity from Identified to Contacted and confirm stage history.
9. Record a meeting activity.
10. Create a high-priority follow-up task due within seven days.
11. Open the dashboard and confirm updates for:
    - pipeline value
    - weighted pipeline value
    - activity count
    - open / due-this-week tasks
    - high-priority / priority opportunities
12. Sign in or switch to Read Only / Technical Analyst and show that sales workflow mutations are denied.
13. Confirm Business Development cannot create admin-only pipeline stages.
14. Show automated evidence:

```text
python -m pytest backend -q -p no:cacheprovider
50 passed

python -m pytest backend/tests/test_week2_rls_permissions.py -q -p no:cacheprovider
7 passed

python -m ruff check backend
All checks passed!

npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
```

## Gate Check

Week 2 gate path:

```text
company -> contact -> opportunity -> stage movement -> activity -> next action -> dashboard update
```

Critical/high defects remaining: 0
