# Week 4 Day 17 Company CSV UI Evidence

Date: 19-08-2026
Branch: `feature/company-csv-ui`
Scope: Intern 2 frontend only - accessible company CSV selection, import feedback, export download, responsive layout, and component tests.

## Implemented

- Added a labeled `.csv` file picker, Import CSV action, and Export CSV action to the Companies page.
- Import shows loading and disabled states, reports the created count, refreshes the company list, and presents safe duplicate and validation feedback for HTTP 409 and HTTP 422 responses.
- Export preserves the backend UTF-8 CSV bytes, uses the server filename when supplied, and starts a browser download.
- Added focused Vitest component coverage for selection, success, refresh, duplicate and validation states, loading/disabled controls, and download behavior.

## Security and data handling

- The UI accepts `.csv` files only and does not inspect, log, or display file contents.
- Backend error details are not reflected to the user; only safe, action-oriented messages are announced.
- The UI is intended for the approved synthetic company dataset only. No real customer data, credentials, or exported files are tracked.

## Verification

From `frontend/`:

```text
npm run test
6 passed

npm run typecheck
passed

npm run lint
passed

npm run build
passed
```

## Manual verification

- Selected `sample-data/companies.csv` and imported it successfully with the announced result: “30 companies imported successfully.”
- Confirmed the company list refreshed after the successful import.
- Re-importing the same file showed the expected duplicate conflict without adding records.
- Export downloaded successfully, opened correctly, and contained 30 company rows.
- Verified the Companies page at desktop, tablet, and mobile widths.
- Verified keyboard access and visible focus for the file picker, Import CSV action, and Export CSV action.

## Remaining TODO

- None for the Day 17 frontend CSV scope.
