"use client";

import { useState } from "react";
import { Building2, Plus } from "lucide-react";

import IcpScorePanel from "@/components/companies/icp-score-panel";
import CompanyCard from "@/components/companies/company-card";
import CompanyCsvActions from "@/components/companies/company-csv-actions";
import CompanyForm from "@/components/companies/company-form";
import { Button } from "@/components/ui/button";
import { EmptyState, ErrorState, LoadingState } from "@/components/ui/async-state";
import { useCompanies } from "@/hooks/use-companies";
import { archiveCompany, createCompany, updateCompany } from "@/lib/api/companies";
import type { Company, CompanyFormValues } from "@/types/company";

export default function CompaniesPage() {
  const { companies, loading, error, setCompanies, refreshCompanies } = useCompanies();
  const [showForm, setShowForm] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [editing, setEditing] = useState<Company | null>(null);

  async function handleAdd(company: CompanyFormValues) {
    try {
      setSubmitError(null);
      const newCompany: Company = await createCompany(company);

      setCompanies((prev) => [...prev, newCompany]);
      setShowForm(false);
    } catch (caughtError) {
      setSubmitError(
        caughtError instanceof Error ? caughtError.message : "Failed to create company."
      );
    }
  }

  async function handleUpdate(values: CompanyFormValues) {
    if (!editing) return;
    try {
      const updated = await updateCompany(editing.id, values);
      setCompanies((items) => items.map((item) => item.id === updated.id ? updated : item));
      setEditing(null);
    } catch (caughtError) {
      setSubmitError(caughtError instanceof Error ? caughtError.message : "Failed to update company.");
    }
  }

  async function handleArchive(company: Company) {
    if (!window.confirm(`Archive ${company.name}? Its record will be hidden, not permanently erased.`)) return;
    try {
      await archiveCompany(company.id);
      setCompanies((items) => items.filter((item) => item.id !== company.id));
    } catch (caughtError) {
      setSubmitError(caughtError instanceof Error ? caughtError.message : "Failed to archive company.");
    }
  }

  return (
    <div className="space-y-5">
      <div>
        <p className="text-sm font-medium text-primary">CRM</p>
        <div className="mt-1 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-normal sm:text-3xl">
              Companies
            </h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-muted-foreground">
              Manage companies, view details, and verify backend persistence after refresh.
            </p>
          </div>

          <Button type="button" onClick={() => setShowForm((prev) => !prev)} className="w-full gap-2 sm:w-auto">
            <Plus className="h-4 w-4" />
            Add Company
          </Button>
        </div>
      </div>

      {showForm ? <CompanyForm onAdd={handleAdd} /> : null}
      {editing ? (
        <CompanyForm
          key={editing.id}
          title={`Edit ${editing.name}`}
          initialValues={{ name: editing.name, domain: editing.domain, industry: editing.industry, country: editing.country }}
          onAdd={handleUpdate}
        />
      ) : null}

      {submitError ? (
        <p role="alert" className="rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {submitError}
        </p>
      ) : null}

      <CompanyCsvActions onImportComplete={refreshCompanies} />

      <IcpScorePanel companies={companies} />

      <section className="rounded-md border bg-card p-4 shadow-sm sm:p-6" aria-labelledby="company-list-heading">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-md bg-muted">
            <Building2 className="h-5 w-5 text-primary" />
          </div>

          <div>
            <h2 id="company-list-heading" className="font-semibold">Company List</h2>
            <p className="text-sm text-muted-foreground">Companies loaded from FastAPI.</p>
          </div>
        </div>

        {loading ? <LoadingState title="Loading companies..." /> : null}

        {error ? <ErrorState title="Companies could not be loaded" description={error} onRetry={refreshCompanies} /> : null}

        {!loading && !error && companies.length === 0 ? (
          <EmptyState title="No companies yet" description="Add a company to start building the CRM." />
        ) : null}

        {!loading && !error && companies.length > 0 ? (
          <div className="space-y-4">
            {companies.map((company) => (
              <CompanyCard
                key={company.id}
                name={company.name}
                domain={company.domain}
                industry={company.industry}
                country={company.country}
                onEdit={() => { setEditing(company); setShowForm(false); }}
                onArchive={() => handleArchive(company)}
              />
            ))}
          </div>
        ) : null}
      </section>
    </div>
  );
}
