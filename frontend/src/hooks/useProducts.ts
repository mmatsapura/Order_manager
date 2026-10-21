"use client";

import { useQuery } from "@tanstack/react-query";
import { apiJson } from "@/lib/api";
import type { ProductPublic } from "@/types/product";

export function useProducts() {
  const query = useQuery({
    queryKey: ["products"],
    queryFn: () => apiJson<ProductPublic[]>("/products"),
  });

  return {
    products: query.data ?? [],
    error: query.error instanceof Error ? query.error.message : null,
  };
}
