"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { HealthPublic } from "@/types/health";

export function useHealth(auto = false) {
  const query = useQuery({
    queryKey: ["health"],
    enabled: auto, // only run by button
    queryFn: async () => {
      const res = await api("/health");
      return (await res.json()) as HealthPublic;
    },
  });

  return {
    health: query.data ?? null,
    error: query.error instanceof Error ? query.error.message : null,
    loading: query.isFetching,
    check: () => query.refetch(), // query on purpose
  };
}
