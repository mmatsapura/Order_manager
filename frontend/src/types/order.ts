export type OrderStatus =
  | "Created"
  | "Queued"
  | "Processing"
  | "Completed"
  | "Failed"
  | "Cancelled";

export type OrderItem = {
  product_id: string;
  name: string;
  price: number;
  quantity: number;
};

export type OrderItemInput = {
  product_id: string;
  quantity: number;
};

export type OrderCreate = {
  customer_name: string;
  customer_email: string;
  items: OrderItemInput[];
};

export type OrderUpdate = {
  status: OrderStatus;
};

export type OrderPublic = {
  order_id: string;
  customer_name: string;
  customer_email: string;
  items: OrderItem[];
  total_price: number;
  status: OrderStatus;
  retry_count: number;
  created_at: string;
  updated_at: string;
};

export type OrderListQuery = {
  email?: string;
  status?: OrderStatus;
  order_id?: string;
  created_from?: string;
  created_to?: string;
  page?: number;
  limit?: number;
};

export type OrderListResponse = {
  items: OrderPublic[];
  total: number;
  page: number;
  limit: number;
};

export type OrderEventPublic = {
  order_id: string;
  from_status: OrderStatus | null;
  to_status: OrderStatus;
  created_at: string;
};
