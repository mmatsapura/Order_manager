"use client";

import { StatusBadge } from "@/components/ui/StatusBadge";
import { useHealth } from "@/hooks/useHealth";

export function HealthPanel({ auto = false }: { auto?: boolean }) {
  const { health, error, loading, check } = useHealth(auto);

  return (
    <div className="health-panel">
      <button type="button" className="btn-secondary" onClick={() => check()} disabled={loading}>
        {loading ? "Checking..." : "Check API health"}
      </button>
      {error && <p className="alert-error">{error}</p>}
      {health && (
        <div className="card">
          <div className="detail-grid">
            <HealthField label="Status" value={health.status} />
            <HealthField label="API" value={health.api} />
            <HealthField label="MongoDB" value={health.mongodb} />
            <HealthField label="RabbitMQ" value={health.rabbitmq} />
            <HealthField label="Redis" value={health.redis} />
          </div>
        </div>
      )}
    </div>
  );
}

function HealthField({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail-field">
      <span className="detail-label">{label}</span>
      <p className="detail-value">
        <StatusBadge value={value} />
      </p>
    </div>
  );
}
