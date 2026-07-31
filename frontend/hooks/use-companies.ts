"use client";

import { useEffect, useState } from "react";

import { getCompanies } from "@/lib/api/companies";
import type { Company } from "@/types/company";

export function useCompanies() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refreshCompanies() {
    try {
      setLoading(true);
      setError(null);
      const data = await getCompanies();
      setCompanies(data);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to load companies");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshCompanies();
  }, []);

  return {
    companies,
    loading,
    error,
    setCompanies,
    refreshCompanies,
  };
}
