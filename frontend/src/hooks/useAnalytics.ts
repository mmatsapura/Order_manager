"use client";

import { useQuery } from "@tanstack/react-query";
import { apiJson } from "@/lib/api";
import type { AnalyticsPublic } from "@/types/analytics";

export function useAnalytics() {
  const query = useQuery({
    queryKey: ["analytics"],
    queryFn: () => apiJson<AnalyticsPublic>("/analytics"),
    refetchInterval: 3000,
  });

  return {
    data: query.data ?? null,
    error: query.error instanceof Error ? query.error.message : null,
  };
}
