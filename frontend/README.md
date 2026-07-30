# Frontend

Next.js frontend for the XY CYBER Growth Intelligence MVP.

## Required Stack

- Next.js
- TypeScript strict mode
- Tailwind CSS
- shadcn/ui
- Chart library for dashboard views

## Current Implementation

- App Router structure.
- Design tokens in `app/globals.css` and `tailwind.config.ts`.
- Login page at `/login`.
- Protected app shell for authenticated routes.
- Responsive navigation for desktop and mobile.
- Placeholder protected pages for dashboard, companies, and contacts.
- Local mock session helper until Supabase Auth is ready.

## Run Locally

PowerShell blocks the `npm.ps1` shim on some Windows machines. Use `npm.cmd`.

```bash
npm.cmd install
npm.cmd run dev
```

Open:

```text
http://localhost:3000/login
```

Use the prefilled demo login form. It stores a local mock session only.

## Required Week 1 Work Still Pending

- Add Supabase client setup.
- Add company/contact list and forms.
- Handle loading, empty, validation, permission, server-error, and success states.
- Integrate with backend company/contact APIs.
- Replace mock auth with Supabase Auth.

## Important Boundary

The frontend must not call the database directly for sensitive calculations or privileged actions. Those belong behind FastAPI endpoints with server-side authorization.
