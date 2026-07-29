import { Building2 } from "lucide-react";

export default function CompaniesPage() {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">CRM</p>
        <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">Companies</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          Placeholder route for the Week 1 create/view company workflow. This page is protected
          and ready for the company API once the schema is applied.
        </p>
      </div>

      <section className="rounded-md border bg-card p-6 shadow-sm">
        <div className="flex max-w-2xl gap-4">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-md bg-muted text-primary">
            <Building2 className="size-6" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-lg font-semibold tracking-normal">Company list coming next</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              The next implementation should add list, create, edit, search, archive, loading,
              empty, validation, permission, and server-error states.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
