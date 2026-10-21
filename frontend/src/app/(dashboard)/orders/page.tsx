"use client";

import { OrderFilters } from "@/components/orders/OrderFilters";
import { OrderTable } from "@/components/orders/OrderTable";

export default function OrdersPage() {
  return (
    <main className="page">
      <h1 className="page-title">Orders</h1>
      <OrderFilters />
      <OrderTable />
    </main>
  );
}
