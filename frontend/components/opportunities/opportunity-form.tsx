"use client";

import { FormEvent, useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import type { Company, Contact } from "@/types/company";
import type { OpportunityFormValues, PipelineStage } from "@/types/opportunity";

const emptyValues: OpportunityFormValues = {
  companyId: "",
  contactId: "",
  stageId: "",
  name: "",
  service: "",
  valueUsd: "0",
  probability: "0",
  expectedCloseDate: "",
  need: "",
  blockers: "",
  competitor: "",
  nextAction: "",
  nextActionDueAt: "",
  lostReason: "",
};

type OpportunityFormProps = {
  companies: Company[];
  contacts: Contact[];
  stages: PipelineStage[];
  initialValues?: OpportunityFormValues;
  submitLabel: string;
  onSubmit: (values: OpportunityFormValues) => Promise<void> | void;
};

export default function OpportunityForm({
  companies,
  contacts,
  stages,
  initialValues,
  submitLabel,
  onSubmit,
}: OpportunityFormProps) {
  const [values, setValues] = useState<OpportunityFormValues>(initialValues ?? emptyValues);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setValues((current) => ({
      ...current,
      companyId: current.companyId || companies[0]?.id || "",
      stageId: current.stageId || stages[0]?.id || "",
    }));
  }, [companies, stages]);

  useEffect(() => {
    if (initialValues) {
      setValues(initialValues);
    }
  }, [initialValues]);

  function updateField(field: keyof OpportunityFormValues, value: string) {
    setValues((current) => ({
      ...current,
      [field]: value,
      contactId: field === "companyId" ? "" : current.contactId,
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const probability = Number(values.probability);
    const valueUsd = Number(values.valueUsd);

    if (!values.companyId || !values.stageId || !values.name.trim()) {
      setError("Company, stage, and opportunity name are required.");
      return;
    }

    if (Number.isNaN(valueUsd) || valueUsd < 0) {
      setError("Value must be zero or greater.");
      return;
    }

    if (Number.isNaN(probability) || probability < 0 || probability > 100) {
      setError("Probability must be between 0 and 100.");
      return;
    }

    try {
      setIsSubmitting(true);
      setError(null);
      await onSubmit({
        ...values,
        name: values.name.trim(),
        service: values.service.trim(),
        need: values.need.trim(),
        blockers: values.blockers.trim(),
        competitor: values.competitor.trim(),
        nextAction: values.nextAction.trim(),
        lostReason: values.lostReason.trim(),
      });

      if (!initialValues) {
        setValues({
          ...emptyValues,
          companyId: companies[0]?.id || "",
          stageId: stages[0]?.id || "",
        });
      }
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to save opportunity.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5 rounded-md border bg-card p-5 shadow-sm">
      <div>
        <h2 className="text-lg font-semibold tracking-normal">
          {initialValues ? "Edit opportunity" : "Create opportunity"}
        </h2>
      </div>

      {error ? (
        <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </p>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-2">
          <Label htmlFor="opportunity-company">Company</Label>
          <select
            id="opportunity-company"
            className="flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm"
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

        <div className="space-y-2">
          <Label htmlFor="opportunity-contact">Contact</Label>
          <select
            id="opportunity-contact"
            className="flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={values.contactId}
            onChange={(event) => updateField("contactId", event.target.value)}
          >
            <option value="">No primary contact</option>
            {contacts
              .filter((contact) => !values.companyId || contact.companyId === values.companyId)
              .map((contact) => (
                <option key={contact.id} value={contact.id}>
                  {contact.firstName} {contact.lastName}
                </option>
              ))}
          </select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="opportunity-stage">Stage</Label>
          <select
            id="opportunity-stage"
            className="flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={values.stageId}
            onChange={(event) => updateField("stageId", event.target.value)}
          >
            {stages.map((stage) => (
              <option key={stage.id} value={stage.id}>
                {stage.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-2 lg:col-span-2">
          <Label htmlFor="opportunity-name">Opportunity name</Label>
          <Input
            id="opportunity-name"
            value={values.name}
            onChange={(event) => updateField("name", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="opportunity-service">Service</Label>
          <Input
            id="opportunity-service"
            value={values.service}
            onChange={(event) => updateField("service", event.target.value)}
          />
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="space-y-2">
          <Label htmlFor="opportunity-value">Value USD</Label>
          <Input
            id="opportunity-value"
            type="number"
            min="0"
            value={values.valueUsd}
            onChange={(event) => updateField("valueUsd", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="opportunity-probability">Probability</Label>
          <Input
            id="opportunity-probability"
            type="number"
            min="0"
            max="100"
            value={values.probability}
            onChange={(event) => updateField("probability", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="opportunity-close-date">Expected close</Label>
          <Input
            id="opportunity-close-date"
            type="date"
            value={values.expectedCloseDate}
            onChange={(event) => updateField("expectedCloseDate", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="opportunity-next-due">Next action due</Label>
          <Input
            id="opportunity-next-due"
            type="datetime-local"
            value={values.nextActionDueAt}
            onChange={(event) => updateField("nextActionDueAt", event.target.value)}
          />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="opportunity-need">Need</Label>
          <textarea
            id="opportunity-need"
            className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={values.need}
            onChange={(event) => updateField("need", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="opportunity-next-action">Next action</Label>
          <textarea
            id="opportunity-next-action"
            className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={values.nextAction}
            onChange={(event) => updateField("nextAction", event.target.value)}
          />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <div className="space-y-2">
          <Label htmlFor="opportunity-blockers">Blockers</Label>
          <Input
            id="opportunity-blockers"
            value={values.blockers}
            onChange={(event) => updateField("blockers", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="opportunity-competitor">Competitor</Label>
          <Input
            id="opportunity-competitor"
            value={values.competitor}
            onChange={(event) => updateField("competitor", event.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="opportunity-lost-reason">Lost reason</Label>
          <Input
            id="opportunity-lost-reason"
            value={values.lostReason}
            onChange={(event) => updateField("lostReason", event.target.value)}
          />
        </div>
      </div>

      <Button type="submit" disabled={isSubmitting || companies.length === 0 || stages.length === 0}>
        {isSubmitting ? "Saving..." : submitLabel}
      </Button>
    </form>
  );
}
