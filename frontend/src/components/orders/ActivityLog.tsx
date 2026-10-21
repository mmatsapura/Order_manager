import type { OrderEventPublic } from "@/types/order";
import { StatusBadge } from "@/components/ui/StatusBadge";

export function ActivityLog({ events }: { events: OrderEventPublic[] }) {
  if (events.length === 0) return <p className="muted">No status changes yet.</p>;
  return (
    <ul className="timeline">
      {events.map((event, i) => (
        <li key={i} className="timeline-item">
          <span className="status-flow">
            {event.from_status ? <StatusBadge value={event.from_status} /> : "—"}
            <span>→</span>
            <StatusBadge value={event.to_status} />
          </span>
          <span className="timeline-time">
            {new Date(event.created_at).toLocaleString()}
          </span>
        </li>
      ))}
    </ul>
  );
}
