from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from app.core.exceptions import EmailTaken, InvalidCredentials
from app.core.security import hash_password, create_access_token, verify_password, decode_access_token
from app.db.redis import RedisDB
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def register(self, data: UserCreate) -> User:
        user = User(email=data.email, hashed_password=hash_password(data.password))
        try:
            return await self.user_repository.create_user(user)
        except DuplicateKeyError:
            raise EmailTaken(data.email)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repository.get_user_by_email(data.email)
        if user is None:
            raise InvalidCredentials()
        if not (user.is_active):
            raise InvalidCredentials()
        if not (verify_password(data.password, user.hashed_password)):
            raise InvalidCredentials()
        token = create_access_token(user.id)
        return TokenResponse(access_token=token)

    async def logout(self, token: str, redis: RedisDB) -> None:
        payload = decode_access_token(token)
        exp = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        ttl = int(((exp - datetime.now(timezone.utc))).total_seconds())
        await redis.blacklist(payload['jti'], ttl)
        return
