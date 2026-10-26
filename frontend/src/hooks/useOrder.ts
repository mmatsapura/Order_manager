"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiJson } from "@/lib/api";
import type { OrderEventPublic, OrderPublic } from "@/types/order";
import type { NotificationPublic } from "@/types/notification";

const CANCELLABLE = new Set(["Created", "Queued", "Processing"]);

export function useOrder(orderId: string) {
  const queryClient = useQueryClient();// 3 parallel queries
  const orderQuery = useQuery({
    queryKey: ["order", orderId],
    queryFn: () => apiJson<OrderPublic>(`/orders/${orderId}`),
    refetchInterval: 3000,
  });
  const eventsQuery = useQuery({
    queryKey: ["order", orderId, "events"],
    queryFn: () => apiJson<OrderEventPublic[]>(`/orders/${orderId}/events`),
    refetchInterval: 3000,
  });
  const notificationsQuery = useQuery({
    queryKey: ["order", orderId, "notifications"],
    queryFn: () => apiJson<NotificationPublic[]>(`/orders/${orderId}/notifications`),
    refetchInterval: 3000,
  });
  const cancelMutation = useMutation({
    mutationFn: () => apiJson(`/orders/${orderId}/cancel`, { method: "POST" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["order", orderId] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
  });
  const requeueMutation = useMutation({
    mutationFn: () =>
      apiJson(`/orders/${orderId}`, {
        method: "PATCH",
        body: JSON.stringify({ status: "Queued" }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["order", orderId] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
    },
  });

  const order = orderQuery.data ?? null;
  const actionError = requeueMutation.error ?? cancelMutation.error;

  return {
    order,
    events: eventsQuery.data ?? [],
    notifications: notificationsQuery.data ?? [],
    error: orderQuery.error instanceof Error ? orderQuery.error.message : null,
    actionError: actionError instanceof Error ? actionError.message : null,
    cancelling: cancelMutation.isPending,
    requeueing: requeueMutation.isPending,
    canCancel: order != null && CANCELLABLE.has(order.status),
    canRequeue: order?.status === "Failed",
    cancel: () => cancelMutation.mutate(),
    requeue: () => requeueMutation.mutate(),
  };
}
