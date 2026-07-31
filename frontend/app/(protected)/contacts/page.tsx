"use client";

import { useState } from "react";
import { Plus, Users } from "lucide-react";

import ContactCard from "@/components/contacts/contact-card";
import ContactForm from "@/components/contacts/contact-form";
import { Button } from "@/components/ui/button";
import { useCompanies } from "@/hooks/use-companies";
import { useContacts } from "@/hooks/use-contacts";
import type { Contact, ContactFormValues } from "@/types/company";

export default function ContactsPage() {
  const { contacts, loading, error } = useContacts();
  const { companies } = useCompanies();
  const [showForm, setShowForm] = useState(false);
  const [contactList, setContactList] = useState<Contact[]>([]);

  function handleAdd(contact: ContactFormValues) {
    const newContact: Contact = {
      id: crypto.randomUUID(),
      ...contact,
    };

    setContactList((prev) => [...prev, newContact]);
    setShowForm(false);
  }

  const allContacts = [...contacts, ...contactList];
  const companyById = new Map(companies.map((company) => [company.id, company.name]));

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">CRM</p>
        <div className="mt-1 flex items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">Contacts</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              Manage company contacts and relationships.
            </p>
          </div>

          <Button type="button" onClick={() => setShowForm((prev) => !prev)} className="gap-2">
            <Plus className="h-4 w-4" />
            Add Contact
          </Button>
        </div>
      </div>

      {showForm ? <ContactForm companies={companies} onAdd={handleAdd} /> : null}

      <section className="rounded-md border bg-card p-6 shadow-sm">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
            <Users className="h-5 w-5 text-primary" />
          </div>

          <div>
            <h2 className="font-semibold">Contact List</h2>
            <p className="text-sm text-muted-foreground">Contacts loaded from mock API.</p>
          </div>
        </div>

        {loading ? <p className="text-sm text-muted-foreground">Loading contacts...</p> : null}

        {error ? (
          <p className="text-sm text-red-500">Failed to load contacts. Please try again.</p>
        ) : null}

        {!loading && !error && allContacts.length === 0 ? (
          <p className="text-sm text-muted-foreground">No contacts found.</p>
        ) : null}

        {!loading && !error && allContacts.length > 0 ? (
          <div className="space-y-4">
            {allContacts.map((contact) => (
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
