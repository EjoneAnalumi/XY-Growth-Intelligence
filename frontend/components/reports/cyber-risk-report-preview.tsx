type CyberRiskReportPreviewProps = {
  htmlPreview: string | null;
};

export function CyberRiskReportPreview({ htmlPreview }: CyberRiskReportPreviewProps) {
  if (!htmlPreview) {
    return (
      <section className="rounded-md border bg-card p-6 text-sm text-muted-foreground">
        Select a generated report to review its server-generated snapshot evidence.
      </section>
    );
  }

  return (
    <iframe
      className="min-h-[42rem] w-full rounded-md border bg-white"
      sandbox=""
      srcDoc={htmlPreview}
      title="Server-generated cyber risk report preview"
    />
  );
}
