"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { CompanyFormValues } from "@/types/company";

type CompanyFormProps = {
  onAdd: (company: CompanyFormValues) => void;
};

export default function CompanyForm({ onAdd }: CompanyFormProps) {
  const [values, setValues] = useState<CompanyFormValues>({
    name: "",
    domain: "",
    industry: "",
    country: "",
  });
  const [error, setError] = useState<string | null>(null);

  function updateField(field: keyof CompanyFormValues, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const cleanedValues = {
      name: values.name.trim(),
      domain: values.domain.trim().toLowerCase(),
      industry: values.industry.trim(),
      country: values.country.trim(),
    };
    const domainRegex = /^[a-z0-9-]+(\.[a-z0-9-]+)+$/;

    if (
      !cleanedValues.name ||
      !cleanedValues.domain ||
      !cleanedValues.industry ||
      !cleanedValues.country
    ) {
      setError("All fields are required.");
      return;
    }

    if (cleanedValues.name.length < 2) {
      setError("Company name must contain at least 2 characters.");
      return;
    }

    if (!domainRegex.test(cleanedValues.domain)) {
      setError("Enter a valid domain such as northstar-robotics.example.");
      return;
    }

    setError(null);
    onAdd(cleanedValues);
    setValues({ name: "", domain: "", industry: "", country: "" });
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 rounded-md border bg-card p-5 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold tracking-normal">Add company</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Use fictional data only. Demo domains should use `.example`.
        </p>
      </div>

      {error ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="company-name">Company name</Label>
          <Input
            id="company-name"
            value={values.name}
            onChange={(event) => updateField("name", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="company-domain">Domain</Label>
          <Input
            id="company-domain"
            value={values.domain}
            onChange={(event) => updateField("domain", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="company-industry">Industry</Label>
          <Input
            id="company-industry"
            value={values.industry}
            onChange={(event) => updateField("industry", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="company-country">Country</Label>
          <Input
            id="company-country"
            value={values.country}
            onChange={(event) => updateField("country", event.target.value)}
          />
        </div>
      </div>

      <Button type="submit">Save company</Button>
    </form>
  );
}
