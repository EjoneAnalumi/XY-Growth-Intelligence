import { UsersRound } from "lucide-react";

export default function ContactsPage() {
  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">CRM</p>
        <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">Contacts</h1>
        <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
          Placeholder route for contact management. It will connect to company-linked contact
          APIs after the backend contract is published.
        </p>
      </div>

      <section className="rounded-md border bg-card p-6 shadow-sm">
        <div className="flex max-w-2xl gap-4">
          <div className="flex size-11 shrink-0 items-center justify-center rounded-md bg-muted text-primary">
            <UsersRound className="size-6" aria-hidden="true" />
          </div>
          <div>
            <h2 className="text-lg font-semibold tracking-normal">Contact list coming next</h2>
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              The Week 1 vertical slice needs create/view behavior for contacts linked to a
              company, including refresh persistence.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
