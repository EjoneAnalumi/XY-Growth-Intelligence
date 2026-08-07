"use client";

import { useEffect, useState } from "react";

import { getDashboardSummary } from "@/lib/api/dashboard";
import type { DashboardSummary } from "@/types/dashboard";

export function useDashboardSummary() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refreshSummary() {
    try {
      setLoading(true);
      setError(null);
      setSummary(await getDashboardSummary());
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshSummary();
  }, []);

  return {
    summary,
    loading,
    error,
    refreshSummary,
  };
}
