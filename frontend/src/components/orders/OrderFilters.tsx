"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { orderQueryToPath, searchToQuery } from "@/lib/order-query";
import type { OrderStatus } from "@/types/order";

const STATUSES: OrderStatus[] = [
  "Created",
  "Queued",
  "Processing",
  "Completed",
  "Failed",
  "Cancelled",
];

export function OrderFilters() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email") ?? "";
  const orderId = params.get("order_id") ?? "";
  const statusParam = params.get("status") ?? "";
  const [search, setSearch] = useState(email || orderId);
  const [status, setStatus] = useState(statusParam);

  useEffect(() => {
    setSearch(email || orderId);
    setStatus(statusParam);
  }, [email, orderId, statusParam]);

  function apply(event: FormEvent) {
    event.preventDefault();
    router.push(orderQueryToPath(searchToQuery(search, status)));
  }

  function clear() {
    setSearch("");
    setStatus("");
    router.push("/orders");
  }

  return (
    <form className="filters" onSubmit={apply}>
      <label className="field">
        Email or order id
        <input
          className="control"
          value={search}
          placeholder="ivan@example.com or order id"
          onChange={(event) => setSearch(event.target.value)}
        />
      </label>
      <label className="field field-status">
        Status
        <select className="control" value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="">All</option>
          {STATUSES.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>
      <div className="filters-actions">
        <button type="submit" className="btn-primary">
          Search
        </button>
        <button type="button" className="btn-secondary" onClick={clear}>
          Clear
        </button>
      </div>
    </form>
  );
}
