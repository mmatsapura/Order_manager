"use client";

import { OrderFilters } from "@/components/orders/OrderFilters";
import { OrderPager } from "@/components/orders/OrderPager";
import { OrderTable } from "@/components/orders/OrderTable";
import { useOrderListParams, useOrders } from "@/hooks/useOrders";

export function OrdersView() {
  const query = useOrderListParams();
  const { data, error } = useOrders(query);
  const filtered = Boolean(query.email || query.order_id || query.status);

  return (
    <main className="page">
      <h1 className="page-title">Orders</h1>
      <OrderFilters />
      <OrderTable data={data} error={error} filtered={filtered} />
      <OrderPager query={query} data={data} />
    </main>
  );
}
