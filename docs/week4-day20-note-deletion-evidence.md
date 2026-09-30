# Week 4 Day 20 - Personal and shared note deletion

Date: 29-09-2026
Branch: `feature/week4-day20-mvp-completion`

## Scope and implementation

Replace note Archive controls with explicit deletion choices. Only the note author or an
Admin may Delete for everyone. Management has no exception for another author's note.
Every authenticated active user, including Read Only, may Delete for myself. This stores
a personal dismissal without changing the shared note, its author, or another user's view.
Shared deletion retains the existing soft-delete/audit mechanism internally.

- `backend/app/api/notes.py`: author/admin shared-delete check, personal-delete endpoint,
  and current-user filtering for list/detail responses.
- `backend/app/services/note_visibility.py`: durable PostgreSQL dismissals and isolated
  in-memory equivalent for unit tests.
- `backend/app/api/inbox.py` and `profiles.py`: dismissed notes no longer appear in the
  current user's unread count or company/contact timeline, including after note edits.
- `frontend/lib/api/notes.ts`, staff notes page, and opportunity activity/task panel:
  Delete for myself and eligible Delete for everyone controls, confirmation explaining
  the audience, error handling, and inbox refresh.
- Mirrored `20260929000002_note_deletion_visibility.sql`: per-user dismissal table,
  foreign keys and RLS; direct authenticated shared update/delete remains denied.
- Backend permission/visibility and RLS tests; frontend role-control tests and a live
  browser test covering a manager's personal deletion followed by admin shared deletion.

## Security

Only synthetic fixtures are used. No credentials are committed. The API takes the user
identity from authentication, never a request-supplied user ID. RLS isolates personal
rows and denies anonymous access. Shared deletion checks ownership on the backend,
not only through button visibility. Existing note editing permissions are unchanged.
Personal deletion persists across refresh/login; there is no restore UI in this scope.

## Validation

- `python -m pytest backend -q --tb=short -p no:cacheprovider` with local Supabase:
  **146 passed**, 10 existing upstream deprecation warnings, 22.55 seconds.
- `cd backend; python -m ruff check .`: **All checks passed**.
- `cd frontend; npm.cmd test`: **9 files, 33 tests passed**.
- `npm.cmd run typecheck`, `npm.cmd run lint`, `npm.cmd run build`: **passed**.
- `npx.cmd playwright test note-deletion.spec.ts --config playwright.live.config.ts`: **1 passed**, 18.8 seconds, real local Auth/database. The generated note was deleted during cleanup.
- Local migration applied successfully. Production frontend build uses existing local
  Supabase public configuration; no environment values are written into evidence.

## Remaining steps

Implementation is complete. Hands-on user acceptance and the requested subsequent
logical commits/push/PR remain pending. Changes are uncommitted. Backend and frontend
are left running at localhost:8000 and localhost:3000 for review.
