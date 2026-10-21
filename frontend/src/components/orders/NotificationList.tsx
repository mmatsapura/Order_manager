import type { NotificationPublic } from "@/types/notification";

export function NotificationList({
  notifications,
}: {
  notifications: NotificationPublic[];
}) {
  if (notifications.length === 0) {
    return <p className="muted">No notifications yet.</p>;
  }
  return (
    <ul className="timeline">
      {notifications.map((n, i) => (
        <li key={i} className="timeline-item">
          <span>{n.type}</span>
          <span className="timeline-time">
            {n.created_at ? new Date(n.created_at).toLocaleString() : "—"}
          </span>
        </li>
      ))}
    </ul>
  );
}
