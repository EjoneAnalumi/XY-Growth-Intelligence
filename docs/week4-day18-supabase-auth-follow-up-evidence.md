# Week 4 Day 18 follow-up: Supabase Auth and staff attribution

Date: 24-08-2026  
Branch: `feature/supabase-auth-attribution`

## Scope

This is a separate follow-up, not Day 19. It replaces the mock role selector with invitation-only Supabase Auth and makes staff identity visible on collaborative CRM work, matching the brief's authentication, profile, role, ownership, and audit requirements.

## Implemented

- Real email/password Supabase sessions with access-token refresh and logout.
- Forgot-password, reset-password, and invitation-acceptance pages.
- Admin-only staff invitations, role assignment, activation/deactivation, and user directory.
- Database provisioning trigger creates every invited profile as Read Only before Admin assignment.
- FastAPI validates the bearer session through Supabase Auth, rejects expired tokens, and loads the active database profile and role.
- Notes display writer names; activities and tasks display their creator; opportunities display creator/updater; stage history displays the staff member who moved it.
- CRM create/update/archive triggers record user, entity, action, and UTC timestamp in `audit_logs`; Admin and Management can view recent events.
- Legacy synthetic Auth seed fields were normalized for the current GoTrue image.

## Verification

- `python -m pytest backend`: 98 passed, 5 skipped (Supabase integration tests gated by environment variables).
- `python -m ruff check backend`: all checks passed.
- `npm.cmd run typecheck`: passed.
- `npm.cmd run lint`: passed with no warnings or errors.
- `npm.cmd run build`: passed and generated 16 routes.
- `npm.cmd test -- --run`: 5 files and 15 tests passed in the completed run. A final repeat reached Vitest startup but hung in the Windows/esbuild process and was stopped; no test failure was reported.
- Local Supabase issued a real Business Development session; FastAPI returned the stored role/name and 9 visible synthetic profiles.
- Admin invitation API created a temporary synthetic Read Only user; the test user was deleted immediately afterward.
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

## Status

The integrated local Auth, invitation, role, profile attribution, and audit flows are implemented. Production email delivery and deployment secrets are environment configuration, not repository content.
