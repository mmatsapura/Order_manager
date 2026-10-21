"use client";

import { HealthPanel } from "@/components/health/HealthPanel";

export default function HealthPage() {
  return (
    <main className="p-8">
      <h1 className="text-xl font-bold">Health</h1>
      <HealthPanel auto />
    </main>
  );
}
