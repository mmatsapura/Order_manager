"use client";

import Link from "next/link";
import { StatusBadge } from "@/components/ui/StatusBadge";
import type { OrderListResponse } from "@/types/order";

export function OrderTable({
  data,
  error,
  filtered,
}: {
  data: OrderListResponse | null;
  error: string | null;
  filtered: boolean;
}) {
  if (error) return <p className="alert-error">{error}</p>;
  if (!data) return <p className="muted">Loading...</p>;
  if (data.items.length === 0) {
    return <p className="muted">{filtered ? "No orders match these filters." : "No orders yet."}</p>;
  }

  return (
    <div className="table-wrap">
      <table className="orders-table">
        <thead>
          <tr>
            <th>Order</th>
            <th>Email</th>
            <th>Products</th>
            <th>Qty</th>
            <th>Status</th>
            <th className="col-total">Total</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map((order) => (
            <tr key={order.order_id}>
              <td className="col-id">
                <Link href={`/orders/${order.order_id}`} className="nav-link">
                  {order.order_id}
                </Link>
              </td>
              <td>{order.customer_email}</td>
              <td>{order.items.map((item) => item.name).join(", ")}</td>
              <td>{order.items.map((item) => item.quantity).join(", ")}</td>
              <td>
                <StatusBadge value={order.status} />
              </td>
              <td className="col-total">{order.total_price.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
