"use client";

import { OrderForm } from "@/components/orders/OrderForm";

export default function NewOrderPage() {
  return (
    <main className="page page-narrow">
      <h1 className="page-title">New order</h1>
      <div className="card">
        <OrderForm />
      </div>
    </main>
  );
}
