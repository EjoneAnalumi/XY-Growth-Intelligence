# Week 1 Day 2 Frontend Evidence

Task:

- Create Next.js app shell.
- Add design tokens.
- Add navigation.
- Add login page.
- Add protected route behavior.

Expected evidence:

- Login screen renders responsively.
- Protected layout renders responsively.

## Implemented

- Next.js App Router frontend foundation.
- TypeScript strict mode.
- Tailwind CSS design tokens.
- shadcn-style local UI primitives for button, input, and label.
- Login page at `/login`.
- Protected app shell for dashboard routes.
- Responsive desktop/sidebar and mobile/menu navigation.
- Placeholder protected pages:
  - `/dashboard`
  - `/companies`
  - `/contacts`
  - `/reports`
- Local mock session behavior until Supabase Auth is ready.

## Verification Commands

Run from `frontend/`:

```bash
npm.cmd install
npm.cmd run typecheck
npm.cmd run lint
npm.cmd run build
```

Latest result:

- TypeScript: passed.
- ESLint: passed.
- Production build: passed.
- Local `/login` HTTP check: returned `200`.

Dependency note:

- `npm audit --audit-level=high` currently reports high-severity advisories in transitive Next/PostCSS/ESLint dependency chains.
- Next was updated to `14.2.35`, the patched stable 14.x line.
- `npm audit fix --force` attempted to move the app to Next 16 and ESLint 10, but that created an unstable peer-dependency/build state for this Day 2 foundation.
- Keep this as a Week 1 dependency risk to revisit before any hosted deployment.

## Local Run

Run from `frontend/`:

```bash
npm.cmd run dev
```

Open:

```text
http://localhost:3000/login
```

## Manual Responsive Check

Check these viewport widths in browser dev tools:

- Mobile: 390 x 844
- Tablet: 768 x 1024
- Desktop: 1440 x 900

Expected login behavior:

- Login form remains readable.
- Form fields and sign-in button fit within the viewport.
- Right-side context panel appears only on larger screens.
- No text overlaps.

Expected protected-layout behavior:

- After sign-in, `/dashboard` renders inside the app shell.
- Desktop shows fixed top bar and left navigation.
- Mobile shows top bar and menu button.
- Navigation links are reachable.
- Sign out returns to `/login`.
- Placeholder dashboard, companies, contacts, and reports pages render without layout overlap.

## Current Limitation

Supabase Auth is not connected yet because the Week 1 database/auth work is still in progress. The current frontend uses a local mock session helper in `frontend/lib/auth.ts`; this should be replaced with Supabase Auth after `profiles` and auth integration are ready.
