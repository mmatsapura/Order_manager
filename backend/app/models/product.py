from datetime import datetime, timezone

from pydantic import BaseModel, Field


class Product(BaseModel):
    id: str | None = None
    name: str
    price: float = Field(gt=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
