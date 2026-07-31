"use client";

import { useEffect, useState } from "react";

import { getCompanies } from "@/lib/api/companies";
import type { Company } from "@/types/company";

export function useCompanies() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadCompanies() {
      try {
        setLoading(true);
        const data = await getCompanies();
        setCompanies(data);
      } catch {
        setError("Failed to load companies");
      } finally {
        setLoading(false);
      }
    }

    loadCompanies();
  }, []);

  return {
    companies,
    loading,
    error,
  };
}
