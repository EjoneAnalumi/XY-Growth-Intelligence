# Week 3 Day 15 Demo Script

Date: 17-08-2026

Branch: `feature/week3-demo-gate`

## Scope

Week 3 gate demo for the safe Cyber Risk Snapshot and report workflow.

## Demo Preconditions

- Backend is running at `http://localhost:8000`.
- Frontend is running at `http://localhost:3000`.
- Use synthetic demo roles only.
- Use the approved `.example` demo target only.

## Demo Flow

1. Sign in as `Technical Analyst`.
2. Open `/security-scans`.
3. Keep the synthetic company ID:
   `10000000-0000-4000-8000-000000000001`.
4. Keep the approved demo target:
   `https://northstar-robotics.example/snapshot`.
5. Confirm approval and run the snapshot.
6. Verify the scan shows structured evidence for:
   - approval
   - DNS
   - TLS
   - HTTP headers
   - SPF
   - DMARC
7. Click `Create report from this snapshot`.
8. On `/reports`, click `Generate from snapshot`.
9. Confirm the generated report preview shows:
   - XY CYBER branding
   - prepared company
   - approved target
   - executive summary
   - findings and evidence
   - methodology and limitations
10. Click `Review`.
11. Sign out and sign in as `Management`.
12. Open `/reports`.
13. Click `Approve` on the reviewed report.
14. Click `Download`.
15. Confirm a PDF downloads and contains the synthetic report evidence.
16. Click `Share internally`.
17. Click `Archive`.

## Expected Gate Result

The Week 3 gate passes when one safe synthetic report is generated from structured snapshot evidence, reviewed, approved, stored, downloaded, shared internally, and archived with role restrictions enforced by the backend.

## Safety Language To Mention

- The report is not a penetration test.
- Observations are not confirmed vulnerabilities.
- The target is approved synthetic demo evidence.
- No real customers, prospects, credentials, or service-role keys are in the repository.
