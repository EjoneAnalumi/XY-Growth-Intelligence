"use client";

import { useEffect, useState } from "react";

import { getPipelineStages } from "@/lib/api/opportunities";
import type { PipelineStage } from "@/types/opportunity";

export function usePipelineStages() {
  const [stages, setStages] = useState<PipelineStage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refreshStages() {
    try {
      setLoading(true);
      setError(null);
      const data = await getPipelineStages();
      setStages(data);
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to load stages");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refreshStages();
  }, []);

  return {
    stages,
    loading,
    error,
    refreshStages,
  };
}
