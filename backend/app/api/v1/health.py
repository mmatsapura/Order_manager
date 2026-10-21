from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.schemas.health import HealthPublic


router = APIRouter(tags=['health'])


@router.get('/health')
async def health(request: Request):
    mongodb = 'ok'
    rabbitmq = 'ok'
    redis = 'ok'
    try:
        await request.app.state.mongo.ping()
    except Exception:
        mongodb = 'error'
    try:
        pass
    except Exception:
        rabbitmq = 'error'
    try:
        pass
    except Exception:
        redis = 'error'
