import type { Company } from "@/types/company";

type CompanyCardProps = Pick<Company, "name" | "domain" | "industry" | "country">;

export default function CompanyCard({ name, domain, industry, country }: CompanyCardProps) {
  return (
    <article className="rounded-md border bg-card p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-base font-semibold tracking-normal">{name}</h3>
          <p className="mt-1 text-sm text-muted-foreground">{domain}</p>
        </div>
        <span className="w-fit rounded-md bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
          {country}
        </span>
      </div>

      <p className="mt-3 text-sm">{industry}</p>
    </article>
  );
}
