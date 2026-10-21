"use client";

import { StatusBadge } from "@/components/ui/StatusBadge";
import { useAnalytics } from "@/hooks/useAnalytics";

export function AnalyticsCards() {
  const { data, error } = useAnalytics();

  if (error) return <p className="alert-error">{error}</p>;
  if (!data) return <p className="muted">Loading...</p>;

  const cards = [
    { label: "Total orders", value: data.total_orders },
    { label: "Processing", value: data.processing_count },
    { label: "Completed", value: data.completed_count },
    { label: "Failed", value: data.failed_count },
    {
      label: "Avg processing (sec)",
      value:
        data.average_processing_seconds == null
          ? "—"
          : data.average_processing_seconds.toFixed(2),
    },
    { label: "Retry attempts", value: data.retry_attempts },
  ];

  const statuses = Object.entries(data.by_status);

  return (
    <>
      <div className="stats-grid">
        {cards.map((card) => (
          <div key={card.label} className="stat-card">
            <span className="detail-label">{card.label}</span>
            <p className="stat-value">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="card">
        <p className="section-label">By status</p>
        {statuses.length === 0 ? (
          <p className="muted">No orders yet.</p>
        ) : (
          <ul className="timeline">
            {statuses.map(([status, count]) => (
              <li key={status} className="timeline-item">
                <StatusBadge value={status} />
                <span>{count}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}