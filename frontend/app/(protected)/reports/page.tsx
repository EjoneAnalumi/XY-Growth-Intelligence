import { FileCheck2 } from "lucide-react";

export default function ReportsPage() {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">Reporting</p>
        <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">Reports</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          Placeholder route for the Cyber Risk Snapshot report workflow. Report preview,
          approval, and download are planned for Week 3.
        </p>
      </div>

      <section className="rounded-md border bg-card p-6 shadow-sm">
        <div className="flex max-w-2xl gap-4">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-md bg-muted text-primary">
            <FileCheck2 className="size-6" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-lg font-semibold tracking-normal">Report workflow pending</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Reports must be generated from structured data, technically reviewed, approved by
              an authorized role, stored, and downloaded manually.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
