"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { ActivityLog } from "@/components/orders/ActivityLog";
import { NotificationList } from "@/components/orders/NotificationList";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { useOrder } from "@/hooks/useOrder";

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

export default function OrderDetailsPage() {
  const params = useParams<{ orderId: string }>();
  const orderId = params.orderId;
  const {
    order,
    events,
    notifications,
    error,
    actionError,
    cancelling,
    requeueing,
    canCancel,
    canRequeue,
    cancel,
    requeue,
  } = useOrder(orderId);

  if (error) {
    return (
      <main className="page page-narrow">
        <p className="alert-error">{error}</p>
      </main>
    );
  }
  if (!order) {
    return (
      <main className="page page-narrow">
        <p className="muted">Loading...</p>
      </main>
    );
  }

  return (
    <main className="page page-narrow">
      <h1 className="page-title">Order</h1>
      <div className="card">
        <div className="detail-header">
          <div>
            <p className="muted col-id">{order.order_id}</p>
            <p className="detail-customer">
              {order.customer_name}{" "}
              <span className="muted">({order.customer_email})</span>
            </p>
          </div>
          <div className="detail-actions">
            <StatusBadge value={order.status} />
            {canCancel && (
              <button
                type="button"
                className="btn-danger"
                onClick={() => cancel()}
                disabled={cancelling}
              >
                {cancelling ? "Cancelling..." : "Cancel order"}
              </button>
            )}
            {canRequeue && (
              <button
                type="button"
                className="btn-primary"
                onClick={() => requeue()}
                disabled={requeueing}
              >
                {requeueing ? "Requeueing..." : "Requeue"}
              </button>
            )}
          </div>
        </div>

        {actionError && <p className="alert-error">{actionError}</p>}

        <div className="detail-grid">
          <div className="detail-field">
            <span className="detail-label">Total</span>
            <p className="detail-value">{order.total_price.toFixed(2)}</p>
          </div>
          <div className="detail-field">
            <span className="detail-label">Retry count</span>
            <p className="detail-value">{order.retry_count}</p>
          </div>
          <div className="detail-field">
            <span className="detail-label">Created</span>
            <p className="detail-value">{formatDate(order.created_at)}</p>
          </div>
          <div className="detail-field">
            <span className="detail-label">Updated</span>
            <p className="detail-value">{formatDate(order.updated_at)}</p>
          </div>
        </div>

        <div className="detail-section">
          <p className="section-label">Items</p>
          <table className="detail-table">
            <thead>
              <tr>
                <th>Product</th>
                <th>Qty</th>
                <th>Price</th>
                <th className="col-total">Line</th>
              </tr>
            </thead>
            <tbody>
              {order.items.map((item, index) => (
                <tr key={`${item.product_id}-${index}`}>
                  <td>{item.name}</td>
                  <td>{item.quantity}</td>
                  <td>{item.price.toFixed(2)}</td>
                  <td className="col-total">
                    {(item.price * item.quantity).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="detail-section">
          <p className="section-label">Activity</p>
          <ActivityLog events={events} />
        </div>

        <div className="detail-section">
          <p className="section-label">Notifications</p>
          <NotificationList notifications={notifications} />
        </div>
      </div>
      <p className="detail-back">
        <Link href="/orders" className="nav-link">
          ← Back to orders
        </Link>
      </p>
    </main>
  );
}
