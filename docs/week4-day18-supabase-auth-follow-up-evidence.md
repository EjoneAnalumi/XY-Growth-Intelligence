# Week 4 Day 18 follow-up: Supabase Auth and staff attribution

Date: 24-08-2026  
Branch: `feature/supabase-auth-attribution`

## Scope

This is a separate follow-up, not Day 19. It replaces the mock role selector with invitation-only Supabase Auth and makes staff identity visible on collaborative CRM work, matching the brief's authentication, profile, role, ownership, and audit requirements.

## Implemented

- Real email/password Supabase sessions with access-token refresh and logout.
- Forgot-password, reset-password, and invitation-acceptance pages.
- Admin-only staff invitations, role assignment, activation/deactivation, and user directory.
- Admin user management now supports editing staff names and email addresses and permanently deleting accounts. Self-deactivation, self-demotion, and self-deletion are rejected by FastAPI.
- The Admin user list uses compact summary rows; editing expands only the selected staff member while status and delete controls remain immediately available.
- Onboarding remains invitation-only; the temporary-password option was removed.
- Database provisioning trigger creates every invited profile as Read Only before Admin assignment.
- FastAPI validates the bearer session through Supabase Auth, rejects expired tokens, and loads the active database profile and role.
- Notes display writer names; activities and tasks display their creator; opportunities display creator/updater; stage history displays the staff member who moved it.
- CRM create/update/archive triggers record user, entity, action, and UTC timestamp in `audit_logs`; Admin and Management can view recent events.
- Legacy synthetic Auth seed fields were normalized for the current GoTrue image.

## Verification

- `python -m pytest backend`: 100 passed, 5 skipped (Supabase integration tests gated by environment variables).
- `python -m ruff check backend`: all checks passed.
- `npm.cmd run typecheck`: passed.
- `npm.cmd run lint`: passed with no warnings or errors.
- `npm.cmd run build`: passed and generated 16 routes.
- `npm.cmd test -- --run`: 6 files and 16 tests passed in the final complete run.
- Local Supabase issued a real Business Development session; FastAPI returned the stored role/name and 9 visible synthetic profiles.
- Admin invitation API created a temporary synthetic Read Only user; the test user was deleted immediately afterward.
- A synthetic user CRUD verification successfully created an invitation, edited the name/email/role, returned 204 on deletion, and confirmed the account disappeared.
- Login, forgot-password, reset-password, invitation-acceptance, and Users routes returned HTTP 200.

## Security

- No public sign-up endpoint exists.
- Passwords are handled only by Supabase Auth and are never stored by the application.
- Service-role credentials remain backend-only and were not printed, documented, or committed.
- New profiles default to Read Only at the database boundary.
- Backend role checks remain authoritative; frontend visibility is not treated as authorization.
- Synthetic `.test` identities only.

## Remaining production configuration

- Configure production Supabase URL/keys through the deployment secret manager.
- Configure approved production redirect URLs and company SMTP for invitation/reset delivery.
- Rotate the seeded local-only demo passwords or omit demo users outside local development.
- Complete a browser screenshot/accessibility evidence pass before final internship submission.

## Local port recovery

The Windows workstation repeatedly accumulated duplicate Next.js servers from different worktrees and an orphaned local-mode Uvicorn listener on `127.0.0.1:8000`. The root README now provides one canonical startup from the `supabase-auth` worktree, loads local Supabase values only into the current process, fixes frontend/backend ports at 3000/8000, and documents safe port inspection and the Windows-restart condition for a listener whose PID no longer exists. Supabase ports remain outside the application-port cleanup scope.

## Status

The integrated local Auth, invitation, role, profile attribution, and audit flows are implemented. Production email delivery and deployment secrets are environment configuration, not repository content.

For the complete cross-feature website handoff, see `docs/week4-day18-website-change-handoff.md`.
