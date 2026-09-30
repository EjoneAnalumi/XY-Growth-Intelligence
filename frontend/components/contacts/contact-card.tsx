import { Button } from "@/components/ui/button";
import Link from "next/link";
import type { Contact } from "@/types/company";

type ContactCardProps = Pick<Contact, "firstName" | "lastName" | "email" | "role"> & {
  id?: string;
  createdAt?: string;
  companyName?: string;
  onEdit?: () => void;
  onArchive?: () => void;
};

export default function ContactCard({
  id,
  createdAt,
  firstName,
  lastName,
  email,
  role,
  companyName,
  onEdit,
  onArchive,
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
      {createdAt && <p className="mt-2 text-xs text-muted-foreground">Created <time dateTime={createdAt}>{new Date(createdAt).toLocaleString()}</time></p>}
      <div className="mt-4 flex gap-2">
        {id && <Button asChild variant="outline"><Link href={`/contacts/${id}`}>Profile</Link></Button>}
        <Button type="button" variant="outline" onClick={onEdit}>Edit</Button>
        <Button type="button" variant="outline" onClick={onArchive}>Archive</Button>
      </div>
    </article>
  );
}
