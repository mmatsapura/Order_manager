"use client";

import { useRouter } from "next/navigation";
import { orderQueryToPath } from "@/lib/order-query";
import type { OrderListQuery, OrderListResponse } from "@/types/order";

export function OrderPager({
  query,
  data,
}: {
  query: OrderListQuery;
  data: OrderListResponse | null;
}) {
  const router = useRouter();
  if (!data) return null;

  const page = data.page;
  const from = data.total === 0 ? 0 : (page - 1) * data.limit + 1;
  const to = Math.min(page * data.limit, data.total);
  const hasPrev = page > 1;
  const hasNext = page * data.limit < data.total;

  function go(nextPage: number) {
    router.push(orderQueryToPath({ ...query, page: nextPage }));
  }

  return (
    <div className="pager">
      <p className="muted">
        {from}–{to} of {data.total}
      </p>
      <div className="pager-actions">
        <button type="button" className="btn-secondary" onClick={() => go(page - 1)} disabled={!hasPrev}>
          Previous
        </button>
        <button type="button" className="btn-secondary" onClick={() => go(page + 1)} disabled={!hasNext}>
          Next
        </button>
      </div>
    </div>
  );
}
