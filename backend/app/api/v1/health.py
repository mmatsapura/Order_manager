from fastapi import APIRouter, Request

from app.schemas.health import HealthPublic


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthPublic)
async def health(request: Request) -> HealthPublic:
    mongodb = "ok"
    rabbitmq = "ok"
    redis = "ok"
    try:
        await request.app.state.mongo.ping()
    except Exception:
        mongodb = "error"
    try:
        await request.app.state.rabbit.ping()
    except Exception:
        rabbitmq = "error"
    try:
        await request.app.state.redis.ping()
    except Exception:
        redis = "error"
    parts = (mongodb, rabbitmq, redis)
    overall = "ok" if all(part == "ok" for part in parts) else "error"
    return HealthPublic(
        status=overall,
        api="ok",
        mongodb=mongodb,
        rabbitmq=rabbitmq,
        redis=redis,
    )
