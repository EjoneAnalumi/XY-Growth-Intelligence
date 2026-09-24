# Week 4 Day 20 Retrospective

Date: 24-09-2026
Branch: `feature/week4-day20-final-handover`

## What worked

The single monorepo and published API contract made it possible to connect the sales
workflow to real Supabase Auth, PostgreSQL and private report Storage. Deterministic
synthetic fixtures allowed calculations, permissions and report content to be verified
without contacting real prospects. Feature branches retained each contributor's history.

## What needed correction

Day 19's PR summary overstated completion relative to its own partial-evidence matrix.
Report seed rows satisfied counts but had no actual PDF objects. Repeated seeding
attempted invalid workflow transitions. Frontend browser fixtures had fallen behind the
Auth migration, and frontend checks were absent from CI. The final report template also
omitted required business/recommendation sections despite existing report tests passing.

## Changes made from those lessons

Seed through the real generator and verify private object retrieval. Test repeated SQL
and report seeding. Test required report sections through PDF text extraction. Keep
frontend typecheck/lint/tests/build in CI. Retain a real-session browser journey and
numeric dashboard comparison, while clearly distinguishing it from mocked responsive
tests. Record unfinished brief requirements as backlog rather than claiming full acceptance.

## Next team's working agreements

For each change, name the acceptance behavior first, test it at its actual boundary,
retain safe evidence, and update the user guide in the same PR. Reconcile PR summaries
with the latest evidence before approval. Use disposable isolated databases for clean
install tests; never reset a colleague's working data to make tests pass. Assign both a
backend/data reviewer and a frontend/product reviewer before expanding scope.

## Material AI assistance

Codex assisted with PR review, seed/report fixes, regression tests, local verification,
and handover drafts. The receiving maintainers must review and understand the changes;
automated checks do not replace human review or supervisor acceptance.
