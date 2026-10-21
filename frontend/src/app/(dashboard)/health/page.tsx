"use client";

import { HealthPanel } from "@/components/health/HealthPanel";

export default function HealthPage() {
  return (
    <main className="page page-narrow">
      <h1 className="page-title">Health</h1>
      <HealthPanel auto />
    </main>
  );
}
