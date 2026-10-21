from fastapi import Depends, Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pymongo.asynchronous.database import AsyncDatabase

from app.core.security import decode_access_token
from app.repositories.user import UserRepository
from app.repositories.product import ProductRepository
from app.repositories.order_event import OrderEventRepository
from app.repositories.notification import NotificationRepository
from app.core.exceptions import InvalidToken
from app.models.user import User
from app.repositories.order import OrderRepository
from app.queue.connection import RabbitMQ
from app.db.redis import RedisDB


bearer_token = HTTPBearer(auto_error=False)


def get_db(request: Request) -> AsyncDatabase:
    return request.app.state.mongo.db


def get_user_repository(db: AsyncDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_product_repository(db: AsyncDatabase = Depends(get_db)) -> ProductRepository:
    return ProductRepository(db)


def get_order_repository(db: AsyncDatabase = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)


def get_rabbit_mq(request: Request) -> RabbitMQ:
    return request.app.state.rabbit


def get_redis(request: Request) -> RedisDB:
    return request.app.state.redis


def get_notification_repository(db: AsyncDatabase = Depends(get_db)) -> NotificationRepository:
    return NotificationRepository(db)


def get_order_event_repository(db: AsyncDatabase = Depends(get_db)) -> OrderEventRepository:
    return OrderEventRepository(db)


async def get_current_user(credentials: (HTTPAuthorizationCredentials | None) = Depends(bearer_token), repo: UserRepository = Depends(get_user_repository), redis: RedisDB = Depends(get_redis)) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail='Unauthorized')
    try:
        payload = decode_access_token(credentials.credentials)
        if await redis.is_blacklisted(payload['jti']):
            raise HTTPException(status_code=401, detail='Invalid token')
        user = await repo.get_user_by_id(payload['sub'])
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')
        if not (user.is_active):
            raise HTTPException(status_code=404, detail='User not found')
        return user
    except InvalidToken:
        raise HTTPException(status_code=401, detail='Invalid token')
