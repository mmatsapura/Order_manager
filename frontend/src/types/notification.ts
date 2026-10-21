export type NotificationType =
  | "Order Completed"
  | "Order Failed"
  | "Order Cancelled";

export type NotificationPublic = {
  order_id: string;
  type: NotificationType;
  message: string | null;
  created_at: string | null;
};
