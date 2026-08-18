import {
  CheckCircle2,
  ClipboardCheck,
  Globe2,
  LockKeyhole,
  MailCheck,
  ShieldAlert,
  Target,
} from "lucide-react";

type CyberRiskReportPreviewProps = {
  htmlPreview?: string | null;
};

type FindingSeverity = "high" | "medium" | "low";

type Finding = {
  title: string;
  severity: FindingSeverity;
  observation: string;
  evidence: string;
};

const findings: Finding[] = [
  {
    title: "DMARC policy is monitoring only",
    severity: "low",
    observation:
      "The approved demo domain publishes a monitoring policy rather than an enforcement policy.",
    evidence: "Mock DNS response: v=DMARC1; p=none; rua=mailto:dmarc@example.invalid",
  },
  {
    title: "Content security policy was not observed",
    severity: "medium",
    observation:
      "The mock HTTPS response did not include a Content-Security-Policy header. This is a potential browser-hardening gap.",
    evidence: "Mock HTTPS headers captured during the approved synthetic snapshot.",
  },
];

const severityStyles: Record<FindingSeverity, string> = {
  high: "border-destructive/30 bg-destructive/10 text-destructive",
  medium: "border-orange-300 bg-orange-50 text-orange-800",
  low: "border-yellow-300 bg-yellow-50 text-yellow-800",
};

function SeverityBadge({ severity }: { severity: FindingSeverity }) {
  return (
    <span
      className={`rounded-full border px-2.5 py-1 text-[0.65rem] font-semibold uppercase ${severityStyles[severity]}`}
    >
      {severity}
    </span>
  );
}

export function CyberRiskReportPreview({ htmlPreview }: CyberRiskReportPreviewProps) {
  if (htmlPreview) {
    return (
      <iframe
        className="min-h-[42rem] w-full rounded-md border bg-white"
        sandbox=""
        srcDoc={htmlPreview}
        title="Server-generated cyber risk report preview"
      />
    );
  }

  return <StaticCyberRiskReportPreview />;
}

function StaticCyberRiskReportPreview() {
  return (
    <article className="overflow-hidden rounded-md border bg-card shadow-sm">
      <header className="bg-secondary px-6 py-7 text-secondary-foreground sm:px-10 sm:py-10">
        <div className="flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="flex items-center gap-3 text-sm font-medium text-primary-foreground/75">
              <ShieldAlert className="size-5 text-accent" aria-hidden="true" />
              XY CYBER
            </div>
            <p className="mt-8 text-xs font-semibold uppercase text-accent">
              Confidential - Internal preview
            </p>
            <h2 className="mt-3 max-w-xl text-3xl font-semibold sm:text-4xl">
              Cyber Risk Snapshot
            </h2>
            <p className="mt-3 max-w-lg text-base leading-7 text-secondary-foreground/75">
              A decision-ready overview of externally observable security posture for demo purposes.
            </p>
          </div>

          <dl className="grid gap-3 rounded-md border border-white/15 bg-white/5 p-4 text-sm sm:min-w-52">
            <div>
              <dt className="text-secondary-foreground/60">Prepared for</dt>
              <dd className="mt-1 font-medium">Northstar Commerce Group</dd>
            </div>
            <div>
              <dt className="text-secondary-foreground/60">Snapshot date</dt>
              <dd className="mt-1 font-medium">17-08-2026</dd>
            </div>
            <div>
              <dt className="text-secondary-foreground/60">Report status</dt>
              <dd className="mt-1 font-medium text-accent">Draft for technical review</dd>
            </div>
          </dl>
        </div>
      </header>

      <div className="space-y-10 px-6 py-8 sm:px-10 sm:py-10">
        <section aria-labelledby="executive-summary">
          <p className="text-xs font-semibold uppercase text-primary">01 - Executive summary</p>
          <div className="mt-4 grid gap-6 lg:grid-cols-[auto_1fr] lg:items-center">
            <div className="flex size-32 shrink-0 flex-col items-center justify-center rounded-full border-8 border-accent bg-accent/10">
              <span className="text-4xl font-semibold">62</span>
              <span className="text-xs font-medium text-muted-foreground">Exposure score</span>
            </div>
            <div>
              <h3 id="executive-summary" className="text-xl font-semibold">
                Moderate external exposure requires planned remediation.
              </h3>
              <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
                This synthetic snapshot identifies email-policy and browser-hardening observations
                on an approved mock target. They should be validated by the technical team before
                they are treated as confirmed security issues.
              </p>
            </div>
          </div>
        </section>

        <section aria-labelledby="findings-heading">
          <p className="text-xs font-semibold uppercase text-primary">02 - Key findings</p>
          <h3 id="findings-heading" className="mt-2 text-xl font-semibold">
            Findings grouped by severity
          </h3>
          <div className="mt-4 grid gap-3">
            {findings.map((finding) => (
              <div key={finding.title} className="rounded-md border bg-background p-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h4 className="font-semibold">{finding.title}</h4>
                    <p className="mt-1 text-sm leading-6 text-muted-foreground">
                      {finding.observation}
                    </p>
                  </div>
                  <SeverityBadge severity={finding.severity} />
                </div>
                <p className="mt-3 border-l-2 border-primary/40 pl-3 text-xs leading-5 text-muted-foreground">
                  <span className="font-semibold text-foreground">Evidence:</span>{" "}
                  {finding.evidence}
                </p>
              </div>
            ))}
          </div>
        </section>

        <div className="grid gap-8 lg:grid-cols-2">
          <section aria-labelledby="email-posture">
            <p className="text-xs font-semibold uppercase text-primary">03 - Email security</p>
            <h3 id="email-posture" className="mt-2 flex items-center gap-2 text-xl font-semibold">
              <MailCheck className="size-5 text-primary" aria-hidden="true" />
              Email security posture
            </h3>
            <dl className="mt-4 divide-y rounded-md border bg-background text-sm">
              <div className="flex items-center justify-between gap-4 p-3">
                <dt>SPF record</dt>
                <dd className="font-medium text-primary">Observed</dd>
              </div>
              <div className="flex items-center justify-between gap-4 p-3">
                <dt>DKIM verification</dt>
                <dd className="font-medium text-muted-foreground">Not assessed</dd>
              </div>
              <div className="flex items-center justify-between gap-4 p-3">
                <dt>DMARC policy</dt>
                <dd className="font-medium text-yellow-800">Monitoring only</dd>
              </div>
            </dl>
          </section>

          <section aria-labelledby="web-posture">
            <p className="text-xs font-semibold uppercase text-primary">04 - Web and TLS</p>
            <h3 id="web-posture" className="mt-2 flex items-center gap-2 text-xl font-semibold">
              <LockKeyhole className="size-5 text-primary" aria-hidden="true" />
              Web and TLS posture
            </h3>
            <dl className="mt-4 divide-y rounded-md border bg-background text-sm">
              <div className="flex items-center justify-between gap-4 p-3">
                <dt>HTTPS availability</dt>
                <dd className="font-medium text-primary">Observed</dd>
              </div>
              <div className="flex items-center justify-between gap-4 p-3">
                <dt>TLS certificate</dt>
                <dd className="font-medium text-primary">Valid demo certificate</dd>
              </div>
              <div className="flex items-center justify-between gap-4 p-3">
                <dt>Security headers</dt>
                <dd className="font-medium text-orange-800">CSP not observed</dd>
              </div>
            </dl>
          </section>
        </div>

        <section aria-labelledby="asset-overview" className="rounded-md bg-muted/60 p-5">
          <p className="text-xs font-semibold uppercase text-primary">05 - Asset overview</p>
          <h3 id="asset-overview" className="mt-2 flex items-center gap-2 text-xl font-semibold">
            <Globe2 className="size-5 text-primary" aria-hidden="true" />
            Public asset overview
          </h3>
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div>
              <p className="text-2xl font-semibold">1</p>
              <p className="text-sm text-muted-foreground">Approved demo domain</p>
            </div>
            <div>
              <p className="text-2xl font-semibold">6</p>
              <p className="text-sm text-muted-foreground">Safe checks completed</p>
            </div>
            <div>
              <p className="text-2xl font-semibold">0</p>
              <p className="text-sm text-muted-foreground">Restricted assets accessed</p>
            </div>
          </div>
        </section>

        <div className="grid gap-8 lg:grid-cols-2">
          <section aria-labelledby="business-impact">
            <p className="text-xs font-semibold uppercase text-primary">06 - Business impact</p>
            <h3 id="business-impact" className="mt-2 text-xl font-semibold">
              Why these observations matter
            </h3>
            <p className="mt-3 text-sm leading-6 text-muted-foreground">
              Email impersonation controls and browser security headers can affect customer trust,
              operational continuity, and evidence readiness. Impact depends on internal
              configuration and must be validated.
            </p>
          </section>
          <section aria-labelledby="recommended-actions">
            <p className="text-xs font-semibold uppercase text-primary">07 - Recommended actions</p>
            <h3 id="recommended-actions" className="mt-2 text-xl font-semibold">
              Prioritized next steps
            </h3>
            <ol className="mt-3 space-y-2 text-sm leading-6 text-muted-foreground">
              <li>
                <span className="font-semibold text-foreground">1.</span> Validate DMARC alignment
                and define a staged enforcement plan.
              </li>
              <li>
                <span className="font-semibold text-foreground">2.</span> Confirm the browser
                security-header baseline with application owners.
              </li>
            </ol>
          </section>
        </div>

        <section
          aria-labelledby="next-engagement"
          className="rounded-md border border-primary/25 bg-primary/5 p-5"
        >
          <p className="text-xs font-semibold uppercase text-primary">08 - Next engagement</p>
          <div className="mt-2 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <h3 id="next-engagement" className="flex items-center gap-2 text-xl font-semibold">
                <Target className="size-5 text-primary" aria-hidden="true" />
                Recommended XY CYBER services
              </h3>
              <p className="mt-2 text-sm leading-6 text-muted-foreground">
                Begin with a focused Email Security and External Exposure Review, followed by an
                Executive Security Workshop to agree owners and remediation milestones.
              </p>
            </div>
            <span className="w-fit rounded-full bg-primary px-3 py-1.5 text-xs font-semibold text-primary-foreground">
              Proposed: 30-minute review
            </span>
          </div>
        </section>

        <section aria-labelledby="methodology" className="border-t pt-8">
          <p className="text-xs font-semibold uppercase text-primary">
            09 - Methodology and limitations
          </p>
          <h3 id="methodology" className="mt-2 flex items-center gap-2 text-xl font-semibold">
            <ClipboardCheck className="size-5 text-primary" aria-hidden="true" />
            Methodology, limitations, and disclaimer
          </h3>
          <div className="mt-3 space-y-3 text-sm leading-6 text-muted-foreground">
            <p>
              Scope was limited to an approved synthetic demo domain and deterministic mock DNS,
              TLS, and HTTPS-header observations. No credential attacks, authentication bypass,
              exploitation, aggressive port scanning, or access to restricted systems was performed.
            </p>
            <p>
              This preview is not a penetration test, assurance statement, or confirmation of
              compromise. Failed or unavailable checks are not presented as findings. Technical
              validation is required before approval or external use.
            </p>
          </div>
        </section>
      </div>

      <footer className="flex flex-col gap-3 border-t bg-muted/50 px-6 py-4 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-10">
        <span>XY CYBER Growth Intelligence - Synthetic report preview only</span>
        <span className="flex items-center gap-1.5">
          <CheckCircle2 className="size-3.5 text-primary" aria-hidden="true" />
          Structured evidence retained for review
        </span>
      </footer>
    </article>
  );
}
