"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { apiJson } from "@/lib/api";
import { orderQueryFromParams, PAGE_SIZE } from "@/lib/order-query";
import type { OrderCreate, OrderListQuery, OrderListResponse } from "@/types/order";

function toPath(query: OrderListQuery): string {
  const params = new URLSearchParams();
  if (query.email) params.set("email", query.email);
  if (query.order_id) params.set("order_id", query.order_id);
  if (query.status) params.set("status", query.status);
  params.set("page", String(query.page ?? 1));
  params.set("limit", String(query.limit ?? PAGE_SIZE));
  return `/orders?${params.toString()}`;
}

export function useOrderListParams(): OrderListQuery {
  return orderQueryFromParams(useSearchParams());
}

export function useOrders(listQuery: OrderListQuery = { page: 1, limit: PAGE_SIZE }) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const query = useQuery({
    queryKey: ["orders", listQuery],
    queryFn: () => apiJson<OrderListResponse>(toPath(listQuery)),
    refetchInterval: 3000,
  });
  const create = useMutation({
    mutationFn: (body: OrderCreate) =>
      apiJson("/orders", { method: "POST", body: JSON.stringify(body) }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["orders"] });
      router.push("/orders");
    },
  });

  return {
    data: query.data ?? null,
    error: query.error instanceof Error ? query.error.message : null,
    createOrder: create.mutateAsync,
  };
}
