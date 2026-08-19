"use client";

import { useState } from "react";
import { Plus, Users } from "lucide-react";

import ContactCard from "@/components/contacts/contact-card";
import ContactForm from "@/components/contacts/contact-form";
import { Button } from "@/components/ui/button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/async-state";
import { useCompanies } from "@/hooks/use-companies";
import { useContacts } from "@/hooks/use-contacts";
import { createContact } from "@/lib/api/contacts";
import type { Contact, ContactFormValues } from "@/types/company";

export default function ContactsPage() {
  const { contacts, loading, error, setContacts, refreshContacts } = useContacts();
  const { companies } = useCompanies();
  const [showForm, setShowForm] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  async function handleAdd(contact: ContactFormValues) {
    try {
      setSubmitError(null);
      const newContact: Contact = await createContact(contact);

      setContacts((prev) => [...prev, newContact]);
      setShowForm(false);
    } catch (caughtError) {
      setSubmitError(
        caughtError instanceof Error ? caughtError.message : "Failed to create contact."
      );
    }
  }

  const companyById = new Map(companies.map((company) => [company.id, company.name]));

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">CRM</p>
        <div className="mt-1 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">Contacts</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              Manage company contacts and verify backend persistence after refresh.
            </p>
          </div>

          <Button type="button" onClick={() => setShowForm((prev) => !prev)} className="w-full gap-2 sm:w-auto">
            <Plus className="h-4 w-4" />
            Add Contact
          </Button>
        </div>
      </div>

      {showForm ? <ContactForm companies={companies} onAdd={handleAdd} /> : null}

      {submitError ? (
        <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {submitError}
        </p>
      ) : null}

      <section className="rounded-md border bg-card p-4 shadow-sm sm:p-6" aria-labelledby="contact-list-heading">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
            <Users className="h-5 w-5 text-primary" />
          </div>

          <div>
            <h2 id="contact-list-heading" className="font-semibold">Contact List</h2>
            <p className="text-sm text-muted-foreground">Contacts loaded from FastAPI.</p>
          </div>
        </div>

        {loading ? <LoadingState title="Loading contacts..." /> : null}

        {error ? <ErrorState title="Contacts could not be loaded" description={error} onRetry={refreshContacts} /> : null}

        {!loading && !error && contacts.length === 0 ? (
          <EmptyState title="No contacts yet" description="Add a contact after creating a company." />
        ) : null}

        {!loading && !error && contacts.length > 0 ? (
          <div className="space-y-4">
            {contacts.map((contact) => (
              <ContactCard
                key={contact.id}
                firstName={contact.firstName}
                lastName={contact.lastName}
                email={contact.email}
                role={contact.role}
                companyName={companyById.get(contact.companyId)}
              />
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}
