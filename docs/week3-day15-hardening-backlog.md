# Week 3 Day 15 Hardening Backlog

Date: 17-08-2026

Branch: `feature/week3-demo-gate`

## Critical

- None identified for the Week 3 demo gate.

## High

- None identified for the Week 3 demo gate.

## Medium

- Run Supabase-backed snapshot/report integration tests with local Supabase environment variables before final Week 3 sign-off.
- Decide whether Week 4 should remove the local in-memory fallback after Supabase runtime persistence is stable.
- Add API regression tests for report status transition error consistency.
- Add permission tests for report file metadata and Storage policies in the Supabase RLS suite.
- Add cleanup fixtures for Supabase-backed report integration tests so repeated test runs do not leave report files or scan rows behind.

## Low

- Add screenshot evidence for desktop and mobile report preview.
- Add accessibility checks for the report preview iframe and status action buttons.
- Improve PDF filename normalization for long company names.
- Add a known-limitations section to the final handover docs for the current lightweight PDF renderer.

## Deferred Out Of Scope

- External emailing or automatic sharing of reports.
- Public deployment.
- Live third-party scanning outside approved demo targets.
- Production-grade vulnerability scanner behavior.
