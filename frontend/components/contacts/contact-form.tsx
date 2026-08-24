"use client";

import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Company, ContactFormValues } from "@/types/company";

type ContactFormProps = {
  companies: Company[];
  onAdd: (contact: ContactFormValues) => void | Promise<void>;
  initialValues?: ContactFormValues;
  title?: string;
};

export default function ContactForm({ companies, onAdd, initialValues, title = "Add contact" }: ContactFormProps) {
  const [values, setValues] = useState<ContactFormValues>(initialValues ?? {
    companyId: companies[0]?.id ?? "",
    firstName: "",
    lastName: "",
    email: "",
    role: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (!values.companyId && companies[0]) {
      setValues((current) => ({ ...current, companyId: companies[0].id }));
    }
  }, [companies, values.companyId]);

  function updateField(field: keyof ContactFormValues, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const cleanedValues = {
      companyId: values.companyId,
      firstName: values.firstName.trim(),
      lastName: values.lastName.trim(),
      email: values.email.trim().toLowerCase(),
      role: values.role.trim(),
    };
    const nameRegex = /^[a-zA-Z\s'-]+$/;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (
      !cleanedValues.companyId ||
      !cleanedValues.firstName ||
      !cleanedValues.lastName ||
      !cleanedValues.email ||
      !cleanedValues.role
    ) {
      setError("All fields are required.");
      setSuccess(null);
      return;
    }

    if (!nameRegex.test(cleanedValues.firstName) || !nameRegex.test(cleanedValues.lastName)) {
      setError("Names can contain only letters, spaces, hyphens, and apostrophes.");
      setSuccess(null);
      return;
    }

    if (!emailRegex.test(cleanedValues.email)) {
      setError("Enter a valid email address.");
      setSuccess(null);
      return;
    }

    if (cleanedValues.role.length < 2) {
      setError("Role must contain at least 2 characters.");
      setSuccess(null);
      return;
    }

    setError(null);
    await onAdd(cleanedValues);
    setSuccess("Contact added successfully.");
    if (!initialValues) setValues({
      companyId: cleanedValues.companyId,
      firstName: "",
      lastName: "",
      email: "",
      role: "",
    });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-md border bg-card p-5 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold tracking-normal">{title}</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Link each contact to a fictional company record.
        </p>
      </div>

      {error ? (
        <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      {success ? (
        <p className="rounded-md border border-primary/30 bg-primary/10 px-3 py-2 text-sm text-primary">
          {success}
        </p>
      ) : null}

      <div className="space-y-2">
        <Label htmlFor="contact-company">Company</Label>
        <select
          id="contact-company"
          className="flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
          value={values.companyId}
          onChange={(event) => updateField("companyId", event.target.value)}
        >
          {companies.map((company) => (
            <option key={company.id} value={company.id}>
              {company.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="contact-first-name">First name</Label>
          <Input
            id="contact-first-name"
            value={values.firstName}
            onChange={(event) => updateField("firstName", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="contact-last-name">Last name</Label>
          <Input
            id="contact-last-name"
            value={values.lastName}
            onChange={(event) => updateField("lastName", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="contact-email">Email</Label>
          <Input
            id="contact-email"
            type="email"
            value={values.email}
            onChange={(event) => updateField("email", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="contact-role">Role</Label>
          <Input
            id="contact-role"
            value={values.role}
            onChange={(event) => updateField("role", event.target.value)}
          />
        </div>
      </div>

      <Button type="submit" disabled={companies.length === 0}>
        {initialValues ? "Save changes" : "Save contact"}
      </Button>
    </form>
  );
}
