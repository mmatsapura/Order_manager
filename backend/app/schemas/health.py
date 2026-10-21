from pydantic import BaseModel


class HealthPublic(BaseModel):
    status: str
    api: str
    mongodb: str
    rabbitmq: str
    redis: str
