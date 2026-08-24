# Frontend

Next.js, TypeScript, Tailwind CSS, and shadcn/ui frontend for the XY CYBER Growth Intelligence MVP.

Use the root [README](../README.md) for the complete clean-install, Supabase, backend, Docker, and shutdown procedure.

## Install and verify

PowerShell can block the `npm.ps1` shim, so use `npm.cmd`:

```powershell
Set-Location frontend
npm.cmd ci
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
npm.cmd run dev
```

Open http://127.0.0.1:3000/login and use the synthetic demo credentials displayed by the form.

## Runtime boundaries

- The frontend calls FastAPI through `NEXT_PUBLIC_API_BASE_URL`.
- The current login stores a local mock session; Supabase Auth is not yet connected.
- Core CRM changes persist in Supabase PostgreSQL when the backend has `DATABASE_URL`; logging out no longer erases them.
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` may contain only the local/hosted anonymous public key. Never expose a service-role key in the frontend.
- Core pages include companies, contacts, opportunities, dashboard, security scans, and reports, with responsive and state-handling coverage.
- Docker Compose currently starts only the backend; run the frontend with npm.
