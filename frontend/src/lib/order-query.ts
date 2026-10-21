import type { OrderListQuery, OrderStatus } from "@/types/order";

export const PAGE_SIZE = 20;

const STATUSES = new Set<OrderStatus>([
  "Created",
  "Queued",
  "Processing",
  "Completed",
  "Failed",
  "Cancelled",
]);

export function orderQueryFromParams(params: URLSearchParams): OrderListQuery {
  const status = params.get("status");
  const page = Number(params.get("page") ?? "1");
  return {
    email: params.get("email") || undefined,
    order_id: params.get("order_id") || undefined,
    status: status && STATUSES.has(status as OrderStatus) ? (status as OrderStatus) : undefined,
    page: Number.isInteger(page) && page >= 1 ? page : 1,
    limit: PAGE_SIZE,
  };
}

const ORDER_ID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function searchToQuery(search: string, status: string): OrderListQuery {
  const value = search.trim();
  const query: OrderListQuery = { page: 1, limit: PAGE_SIZE };
  if (ORDER_ID.test(value)) query.order_id = value;
  else if (value) query.email = value;
  if (STATUSES.has(status as OrderStatus)) query.status = status as OrderStatus;
  return query;
}

export function orderQueryToPath(query: OrderListQuery): string {
  const params = new URLSearchParams();
  if (query.email) params.set("email", query.email);
  if (query.order_id) params.set("order_id", query.order_id);
  if (query.status) params.set("status", query.status);
  if (query.page && query.page > 1) params.set("page", String(query.page));
  const qs = params.toString();
  return qs ? `/orders?${qs}` : "/orders";
}
