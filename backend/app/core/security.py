from datetime import datetime, timedelta, timezone
import uuid

import jwt
from pwdlib import PasswordHash

from app.core.config import settings
from app.core.exceptions import InvalidToken


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {'sub': user_id, 'jti': str(uuid.uuid4()), 'type': 'access', 'iat': now, 'exp': (now + timedelta(minutes=settings.jwt_expire_minutes))}
    return jwt.encode(payload=payload, key=settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm], options={'require': [*('sub', 'jti', 'iat', 'exp')]})
        if payload.get('type') != 'access':
            raise jwt.InvalidTokenError('Invalid token type')
        return payload
    except jwt.InvalidTokenError as exc:
        raise InvalidToken() from exc
