import { Activity, Building2, CalendarClock, FileCheck2, TrendingUp } from "lucide-react";

const kpis = [
  { label: "Prospects", value: "10", detail: "Synthetic Week 1 seed target", icon: Building2 },
  { label: "Active opportunities", value: "0", detail: "Starts in Week 2", icon: TrendingUp },
  { label: "Follow-ups due", value: "0", detail: "Task module pending", icon: CalendarClock },
  { label: "Reports ready", value: "0", detail: "Report workflow starts Week 3", icon: FileCheck2 }
];

const nextSteps = [
  "Connect Supabase Auth when profiles are ready.",
  "Build company and contact list screens against the API contract.",
  "Replace placeholder metrics with backend dashboard endpoints."
];

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <p className="text-sm font-medium text-primary">Protected workspace</p>
        <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">
          Growth Intelligence dashboard
        </h1>
        <p className="max-w-3xl text-sm leading-6 text-muted-foreground">
          Placeholder management view for Week 1. The protected layout and navigation render now;
          live CRM data arrives after Supabase and company/contact APIs are integrated.
        </p>
      </div>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {kpis.map((item) => {
          const Icon = item.icon;

          return (
            <article key={item.label} className="rounded-md border bg-card p-4 shadow-sm">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">{item.label}</p>
                  <p className="mt-2 text-3xl font-semibold tracking-normal">{item.value}</p>
                </div>
                <div className="flex size-10 items-center justify-center rounded-md bg-muted text-primary">
                  <Icon className="size-5" aria-hidden="true" />
                </div>
              </div>
              <p className="mt-4 text-sm text-muted-foreground">{item.detail}</p>
            </article>
          );
        })}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr]">
        <article className="rounded-md border bg-card p-5 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex size-10 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <Activity className="size-5" aria-hidden="true" />
            </div>
            <div>
              <h2 className="text-lg font-semibold tracking-normal">Today&apos;s implementation focus</h2>
              <p className="text-sm text-muted-foreground">Week 1, Day 2 frontend foundation</p>
            </div>
          </div>

          <div className="mt-5 overflow-hidden rounded-md border">
            <table className="w-full min-w-[560px] text-left text-sm">
              <thead className="bg-muted text-muted-foreground">
                <tr>
                  <th className="px-4 py-3 font-medium">Area</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Evidence</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                <tr>
                  <td className="px-4 py-3">App shell</td>
                  <td className="px-4 py-3">Ready</td>
                  <td className="px-4 py-3">Protected layout renders</td>
                </tr>
                <tr>
                  <td className="px-4 py-3">Navigation</td>
                  <td className="px-4 py-3">Ready</td>
                  <td className="px-4 py-3">Desktop and mobile links</td>
                </tr>
                <tr>
                  <td className="px-4 py-3">Supabase Auth</td>
                  <td className="px-4 py-3">Mocked</td>
                  <td className="px-4 py-3">Local session placeholder</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article className="rounded-md border bg-card p-5 shadow-sm">
          <h2 className="text-lg font-semibold tracking-normal">Next integration steps</h2>
          <ul className="mt-4 space-y-3">
            {nextSteps.map((step) => (
              <li key={step} className="flex gap-3 text-sm leading-6">
                <span className="mt-2 size-2 shrink-0 rounded-full bg-accent" />
                <span>{step}</span>
              </li>
            ))}
          </ul>
        </article>
      </section>
    </div>
  );
}
