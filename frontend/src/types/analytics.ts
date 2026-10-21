export type AnalyticsPublic = {
  total_orders: number;
  processing_count: number;
  failed_count: number;
  completed_count: number;
  average_processing_seconds: number | null;
  retry_attempts: number;
  by_status: Record<string, number>;
};
