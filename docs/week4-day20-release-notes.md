# Week 4 Day 20 Internship Release Notes

Date: 24-09-2026
Branch: `feature/week4-day20-final-handover`
Tag: `v0.1.0-internship.1`
Classification: local synthetic MVP prerelease; human review and complete brief acceptance pending.

## Included

- Preserves colleague Day 19 work from PR #30 on top of latest main.
- Replaces five empty report placeholders with real branded HTML/PDF generation and private
  Storage objects; repeat seeding verifies objects and preserves ordered workflow states.
- Adds report exposure heuristic, email/web/TLS posture, asset scope, business impact,
  recommended actions and service/next-engagement sections with regression tests.
- Adds real-session browser workflow/CSV acceptance, synthetic screenshots, PDF and dashboard
  comparison evidence; labels the ICP selector for accessibility.
- Adds frontend typecheck/lint/test/build CI alongside backend CI.
- Provides operator/demo guide, architecture/operations, retrospective, limitations and backlog.

## Install / upgrade

Use root README. New installations run SQL migrations/seed, then `python -m app.seed_reports`
from backend/ with local credentials in the environment. Existing databases should not be
reset for normal startup. Apply pending migrations first; the bootstrap upgrades only the
five exact file-less synthetic Day 19 placeholders. No schema migration is added here.

## Review and transfer

Use the combined Day 20 PR to review the Day 19 commits and corrections together; PR #30
remains open until the maintainers decide how to close or merge it. Do not double-apply its
changes. This tag identifies the exact handover snapshot, not a production launch.

See [evidence](week4-day20-handover-evidence.md), [operator guide](week4-day20-demo-user-guide.md)
and [known limitations/backlog](week4-day20-limitations-backlog.md). Remaining detailed brief
requirements are not relabeled optional. No hosted secrets, real data, public deployment,
external email delivery or repository ownership transfer are included.
