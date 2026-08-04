"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { BriefcaseBusiness, Plus, Save, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCompanies } from "@/hooks/use-companies";
import { useContacts } from "@/hooks/use-contacts";
import { useOpportunities } from "@/hooks/use-opportunities";
import {
  createOpportunity,
  deleteOpportunity,
  updateOpportunity,
} from "@/lib/api/opportunities";
import type { Opportunity, OpportunityFormValues } from "@/types/opportunity";
import { cn } from "@/lib/utils";

const emptyForm: OpportunityFormValues = {
  companyId: "",
  contactId: "",
  stageId: "",
  name: "",
  service: "",
  valueUsd: "0",
  probability: "0",
  expectedCloseDate: "",
  ownerId: "",
  need: "",
  blockers: "",
  competitor: "",
  nextAction: "",
  nextActionDueAt: "",
  lostReason: "",
};

function money(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function dateTimeLocal(value: string) {
  if (!value) {
    return "";
  }

  return value.slice(0, 16);
}

function formFromOpportunity(opportunity: Opportunity): OpportunityFormValues {
  return {
    companyId: opportunity.companyId,
    contactId: opportunity.contactId,
    stageId: opportunity.stageId,
    name: opportunity.name,
    service: opportunity.service,
    valueUsd: String(opportunity.valueUsd),
    probability: String(opportunity.probability),
    expectedCloseDate: opportunity.expectedCloseDate,
    ownerId: opportunity.ownerId,
    need: opportunity.need,
    blockers: opportunity.blockers,
    competitor: opportunity.competitor,
    nextAction: opportunity.nextAction,
    nextActionDueAt: dateTimeLocal(opportunity.nextActionDueAt),
    lostReason: opportunity.lostReason,
  };
}

export default function OpportunitiesPage() {
  const { opportunities, loading, error, setOpportunities } = useOpportunities();
  const { companies } = useCompanies();
  const { contacts } = useContacts();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [values, setValues] = useState<OpportunityFormValues>(emptyForm);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const selectedOpportunity = opportunities.find((opportunity) => opportunity.id === selectedId);
  const companiesById = useMemo(
    () => new Map(companies.map((company) => [company.id, company.name])),
    [companies]
  );
  const contactsById = useMemo(
    () =>
      new Map(
        contacts.map((contact) => [
          contact.id,
          `${contact.firstName} ${contact.lastName}`.trim(),
        ])
      ),
    [contacts]
  );

  useEffect(() => {
    if (!selectedId && !isCreating && opportunities[0]) {
      setSelectedId(opportunities[0].id);
    }
  }, [isCreating, opportunities, selectedId]);

  useEffect(() => {
    if (selectedOpportunity && !isCreating) {
      setValues(formFromOpportunity(selectedOpportunity));
    }
  }, [isCreating, selectedOpportunity]);

  function updateField(field: keyof OpportunityFormValues, value: string) {
    setValues((current) => ({ ...current, [field]: value }));
  }

  function startCreate() {
    setIsCreating(true);
    setSelectedId(null);
    setSubmitError(null);
    setValues({
      ...emptyForm,
      companyId: companies[0]?.id ?? "",
      contactId: contacts[0]?.id ?? "",
    });
  }

  function validate() {
    if (!values.companyId || !values.stageId.trim() || !values.name.trim()) {
      return "Company, stage ID, and name are required.";
    }

    const probability = Number(values.probability);
    const valueUsd = Number(values.valueUsd);

    if (!Number.isFinite(valueUsd) || valueUsd < 0) {
      return "Value must be zero or greater.";
    }

    if (!Number.isInteger(probability) || probability < 0 || probability > 100) {
      return "Probability must be a whole number from 0 to 100.";
    }

    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const validationError = validate();

    if (validationError) {
      setSubmitError(validationError);
      return;
    }

    try {
      setSubmitError(null);

      if (isCreating) {
        const created = await createOpportunity(values);
        setOpportunities((current) => [...current, created]);
        setSelectedId(created.id);
        setIsCreating(false);
        return;
      }

      if (!selectedId) {
        return;
      }

      const updated = await updateOpportunity(selectedId, values);
      setOpportunities((current) =>
        current.map((opportunity) => (opportunity.id === updated.id ? updated : opportunity))
      );
      setSelectedId(updated.id);
    } catch (caughtError) {
      setSubmitError(
        caughtError instanceof Error ? caughtError.message : "Failed to save opportunity."
      );
    }
  }

  async function handleDelete() {
    if (!selectedId) {
      return;
    }

    try {
      setSubmitError(null);
      await deleteOpportunity(selectedId);
      setOpportunities((current) => current.filter((opportunity) => opportunity.id !== selectedId));
      setSelectedId(null);
      setValues(emptyForm);
    } catch (caughtError) {
      setSubmitError(
        caughtError instanceof Error ? caughtError.message : "Failed to delete opportunity."
      );
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">Pipeline</p>
        <div className="mt-1 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">
              Opportunities
            </h1>
          </div>

          <Button type="button" onClick={startCreate} className="w-fit gap-2">
            <Plus className="h-4 w-4" />
            Add Opportunity
          </Button>
        </div>
      </div>

      {error ? <p className="text-sm text-red-500">{error}</p> : null}

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(360px,0.7fr)]">
        <section className="rounded-md border bg-card p-4 shadow-sm">
          <div className="mb-4 flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
              <BriefcaseBusiness className="h-5 w-5 text-primary" />
            </div>
            <h2 className="font-semibold">Opportunity Table</h2>
          </div>

          {loading ? <p className="text-sm text-muted-foreground">Loading opportunities...</p> : null}

          {!loading && !error && opportunities.length === 0 ? (
            <p className="text-sm text-muted-foreground">No opportunities found.</p>
          ) : null}

          {!loading && opportunities.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-[920px] w-full table-fixed text-left text-sm">
                <thead className="border-b text-xs uppercase text-muted-foreground">
                  <tr>
                    <th className="w-[220px] px-3 py-3 font-medium">Name</th>
                    <th className="w-[180px] px-3 py-3 font-medium">Company</th>
                    <th className="w-[140px] px-3 py-3 font-medium">Service</th>
                    <th className="w-[120px] px-3 py-3 font-medium">Value</th>
                    <th className="w-[110px] px-3 py-3 font-medium">Probability</th>
                    <th className="w-[140px] px-3 py-3 font-medium">Weighted</th>
                    <th className="w-[150px] px-3 py-3 font-medium">Close Date</th>
                  </tr>
                </thead>
                <tbody>
                  {opportunities.map((opportunity) => (
                    <tr
                      key={opportunity.id}
                      className={cn(
                        "cursor-pointer border-b last:border-0 hover:bg-muted/60",
                        selectedId === opportunity.id && !isCreating ? "bg-muted" : ""
                      )}
                      onClick={() => {
                        setIsCreating(false);
                        setSelectedId(opportunity.id);
                        setSubmitError(null);
                      }}
                    >
                      <td className="truncate px-3 py-3 font-medium">{opportunity.name}</td>
                      <td className="truncate px-3 py-3">
                        {companiesById.get(opportunity.companyId) ?? opportunity.companyId}
                      </td>
                      <td className="truncate px-3 py-3">{opportunity.service || "-"}</td>
                      <td className="px-3 py-3">{money(opportunity.valueUsd)}</td>
                      <td className="px-3 py-3">{opportunity.probability}%</td>
                      <td className="px-3 py-3">{money(opportunity.weightedValueUsd)}</td>
                      <td className="px-3 py-3">{opportunity.expectedCloseDate || "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </section>

        <section className="rounded-md border bg-card p-5 shadow-sm">
          <div className="mb-4">
            <h2 className="font-semibold">{isCreating ? "Create Opportunity" : "Detail View"}</h2>
          </div>

          {!isCreating && !selectedOpportunity ? (
            <p className="text-sm text-muted-foreground">Select an opportunity.</p>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-4">
              {submitError ? (
                <p className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {submitError}
                </p>
              ) : null}

              <div className="space-y-2">
                <Label htmlFor="opportunity-name">Name</Label>
                <Input
                  id="opportunity-name"
                  value={values.name}
                  onChange={(event) => updateField("name", event.target.value)}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="opportunity-company">Company</Label>
                  <select
                    id="opportunity-company"
                    className="flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
                    value={values.companyId}
                    onChange={(event) => updateField("companyId", event.target.value)}
                  >
                    <option value="">Select company</option>
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
                    className="flex h-10 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
                    value={values.contactId}
                    onChange={(event) => updateField("contactId", event.target.value)}
                  >
                    <option value="">No contact</option>
                    {contacts.map((contact) => (
                      <option key={contact.id} value={contact.id}>
                        {contactsById.get(contact.id)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="opportunity-stage">Stage ID</Label>
                <Input
                  id="opportunity-stage"
                  value={values.stageId}
                  onChange={(event) => updateField("stageId", event.target.value)}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="opportunity-service">Service</Label>
                  <Input
                    id="opportunity-service"
                    value={values.service}
                    onChange={(event) => updateField("service", event.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="opportunity-owner">Owner ID</Label>
                  <Input
                    id="opportunity-owner"
                    value={values.ownerId}
                    onChange={(event) => updateField("ownerId", event.target.value)}
                  />
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <div className="space-y-2">
                  <Label htmlFor="opportunity-value">Value USD</Label>
                  <Input
                    id="opportunity-value"
                    type="number"
                    min="0"
                    step="0.01"
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
                    step="1"
                    value={values.probability}
                    onChange={(event) => updateField("probability", event.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="opportunity-close-date">Close Date</Label>
                  <Input
                    id="opportunity-close-date"
                    type="date"
                    value={values.expectedCloseDate}
                    onChange={(event) => updateField("expectedCloseDate", event.target.value)}
                  />
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <TextAreaField
                  id="opportunity-need"
                  label="Need"
                  value={values.need}
                  onChange={(value) => updateField("need", value)}
                />
                <TextAreaField
                  id="opportunity-blockers"
                  label="Blockers"
                  value={values.blockers}
                  onChange={(value) => updateField("blockers", value)}
                />
                <TextAreaField
                  id="opportunity-competitor"
                  label="Competitor"
                  value={values.competitor}
                  onChange={(value) => updateField("competitor", value)}
                />
                <TextAreaField
                  id="opportunity-lost-reason"
                  label="Lost Reason"
                  value={values.lostReason}
                  onChange={(value) => updateField("lostReason", value)}
                />
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="opportunity-next-action">Next Action</Label>
                  <Input
                    id="opportunity-next-action"
                    value={values.nextAction}
                    onChange={(event) => updateField("nextAction", event.target.value)}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="opportunity-next-action-due">Next Action Due</Label>
                  <Input
                    id="opportunity-next-action-due"
                    type="datetime-local"
                    value={values.nextActionDueAt}
                    onChange={(event) => updateField("nextActionDueAt", event.target.value)}
                  />
                </div>
              </div>

              {selectedOpportunity && !isCreating ? (
                <dl className="grid gap-3 border-t pt-4 text-sm sm:grid-cols-2">
                  <div>
                    <dt className="text-muted-foreground">ID</dt>
                    <dd className="break-all">{selectedOpportunity.id}</dd>
                  </div>
                  <div>
                    <dt className="text-muted-foreground">Updated</dt>
                    <dd>{new Date(selectedOpportunity.updatedAt).toLocaleString()}</dd>
                  </div>
                </dl>
              ) : null}

              <div className="flex flex-wrap gap-3">
                <Button type="submit" className="gap-2">
                  <Save className="h-4 w-4" />
                  Save
                </Button>

                {!isCreating && selectedId ? (
                  <Button type="button" variant="outline" onClick={handleDelete} className="gap-2">
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </Button>
                ) : null}
              </div>
            </form>
          )}
        </section>
      </div>
    </div>
  );
}

function TextAreaField({
  id,
  label,
  value,
  onChange,
}: {
  id: string;
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <textarea
        id={id}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
      />
    </div>
  );
}
