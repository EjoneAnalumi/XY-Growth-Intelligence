# Frontend

Next.js has not been initialized yet.

This directory is intentionally a placeholder until frontend foundation work begins.

## Required Stack

- Next.js
- TypeScript strict mode
- Tailwind CSS
- shadcn/ui
- Chart library for dashboard views

## Required Week 1 Work

- Initialize Next.js app.
- Add responsive app shell.
- Add Supabase client setup.
- Add login page.
- Add protected route behavior.
- Add company/contact list and forms.
- Handle loading, empty, validation, permission, server-error, and success states.

## Important Boundary

The frontend must not call the database directly for sensitive calculations or privileged actions. Those belong behind FastAPI endpoints with server-side authorization.
