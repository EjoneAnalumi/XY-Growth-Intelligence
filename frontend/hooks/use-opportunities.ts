"use client";

import { useEffect, useState } from "react";

import { getOpportunities } from "@/lib/api/opportunities";
import type { Opportunity } from "@/types/opportunity";

export function useOpportunities() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refreshOpportunities() {
    try {
      setLoading(true);
      setError(null);
      const data = await getOpportunities();
      setOpportunities(data);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to load opportunities");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshOpportunities();
  }, []);

  return {
    opportunities,
    loading,
    error,
    setOpportunities,
    refreshOpportunities,
  };
}
