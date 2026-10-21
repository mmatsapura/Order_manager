from pydantic import BaseModel


class AnalyticsPublic(BaseModel):
    total_orders: int
    processing_count: int
    failed_count: int
    completed_count: int
    average_processing_seconds: (float | None)
    retry_attempts: int
    by_status: dict[(str, int)]
