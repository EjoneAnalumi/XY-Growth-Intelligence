import type { Contact } from "@/types/company";

type ContactCardProps = Pick<Contact, "firstName" | "lastName" | "email" | "role"> & {
  companyName?: string;
};

export default function ContactCard({
  firstName,
  lastName,
  email,
  role,
  companyName,
}: ContactCardProps) {
  return (
    <article className="rounded-md border bg-card p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-base font-semibold tracking-normal">
            {firstName} {lastName}
          </h3>
          <p className="mt-1 text-sm text-muted-foreground">{email}</p>
        </div>
        <span className="w-fit rounded-md bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
          {role}
        </span>
      </div>

      {companyName ? <p className="mt-3 text-sm text-muted-foreground">{companyName}</p> : null}
    </article>
  );
}
