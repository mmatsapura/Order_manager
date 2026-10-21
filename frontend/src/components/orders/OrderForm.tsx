"use client";

import { useState } from "react";
import { useFieldArray, useForm } from "react-hook-form";
import { useOrders } from "@/hooks/useOrders";
import { useProducts } from "@/hooks/useProducts";

type FormValues = {
  customer_name: string;
  customer_email: string;
  items: { product_id: string; quantity: number }[];
};

export function OrderForm() {
  const { createOrder } = useOrders();
  const { products, error: productsError } = useProducts();
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, control, formState } = useForm<FormValues>({
    defaultValues: {
      items: [{ product_id: "", quantity: 1 }],
    },
  });
  const { fields, append, remove } = useFieldArray({
    control,
    name: "items",
  });

  async function onSubmit(values: FormValues) {
    setError(null);
    try {
      await createOrder({
        customer_name: values.customer_name,
        customer_email: values.customer_email,
        items: values.items.map((item) => ({
          product_id: item.product_id,
          quantity: Number(item.quantity),
        })),
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Create failed");
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="form">
      {(productsError || error) && (
        <p className="alert-error">{productsError || error}</p>
      )}

      <div className="form-row">
        <label className="field">
          Customer name
          <input
            placeholder="Ivan"
            className="control"
            {...register("customer_name", { required: true })}
          />
        </label>
        <label className="field">
          Email
          <input
            type="email"
            placeholder="ivan@example.com"
            className="control"
            {...register("customer_email", { required: true })}
          />
        </label>
      </div>

      <div className="line-items">
        <p className="section-label">Products</p>
        {fields.map((field, index) => (
          <div key={field.id} className="line-item">
            <select
              className="control"
              {...register(`items.${index}.product_id`, { required: true })}
            >
              <option value="">Select product</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.price})
                </option>
              ))}
            </select>
            <input
              type="number"
              min={1}
              className="control control-qty"
              {...register(`items.${index}.quantity`, { required: true, min: 1 })}
            />
            {fields.length > 1 && (
              <button type="button" className="btn-remove" onClick={() => remove(index)}>
                Remove
              </button>
            )}
          </div>
        ))}
        <button
          type="button"
          className="btn-text"
          onClick={() => append({ product_id: "", quantity: 1 })}
        >
          + Add product
        </button>
      </div>

      <button
        type="submit"
        disabled={formState.isSubmitting}
        className="btn-primary btn-primary-end"
      >
        {formState.isSubmitting ? "Creating..." : "Create order"}
      </button>
    </form>
  );
}
