from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.order import router as orders_router
from app.api.v1.product import router as products_router
from app.core.config import settings
from app.db.db import MongoDB
from app.db.redis import RedisDB
from app.queue.connection import RabbitMQ


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo = MongoDB(settings.mongodb_url, settings.mongodb_database)
    rabbit = RabbitMQ(settings.rabbitmq_url)
    redis = RedisDB(settings.redis_url)
    await mongo.connect()
    await rabbit.connect()
    await redis.connect()
    app.state.mongo = mongo
    app.state.rabbit = rabbit
    app.state.redis = redis
    try:
        yield
    finally:
        await rabbit.close()
        await mongo.close()
        await redis.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(analytics_router)
app.include_router(health_router)
