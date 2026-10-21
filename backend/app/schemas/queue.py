from pydantic import BaseModel


class QueueMessage(BaseModel):
    order_id: str
    attempt: int = 0
