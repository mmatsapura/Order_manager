import pytest
from unittest.mock import AsyncMock

from pymongo.errors import DuplicateKeyError

from app.core.exceptions import EmailTaken, InvalidCredentials
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.auth import AuthService


def make_user(password="secret1", **overrides):
    data = dict(
        id="user-1",
        email="ann@example.com",
        hashed_password=hash_password(password),
        is_active=True,
    )
    data.update(overrides)
    return User(**data)


@pytest.fixture
def repo():
    return AsyncMock()


async def test_register_stores_hashed_password(repo):
    repo.create_user.side_effect = lambda new_user: new_user

    created = await AuthService(repo).register(UserCreate(email="ann@example.com", password="secret1"))

    assert created.hashed_password != "secret1"
    assert verify_password("secret1", created.hashed_password)


async def test_register_duplicate_email(repo):
    repo.create_user.side_effect = DuplicateKeyError("duplicate email")

    with pytest.raises(EmailTaken):
        await AuthService(repo).register(UserCreate(email="ann@example.com", password="secret1"))


async def test_login_returns_token(repo):
    repo.get_user_by_email.return_value = make_user()

    token = await AuthService(repo).login(LoginRequest(email="ann@example.com", password="secret1"))

    assert token.access_token
    assert token.token_type == "bearer"


@pytest.mark.parametrize(
    "found",
    [None, make_user(password="other-pass"), make_user(is_active=False)],
    ids=["unknown user", "wrong password", "inactive user"],
)
async def test_login_rejects_bad_user(repo, found):
    repo.get_user_by_email.return_value = found

    with pytest.raises(InvalidCredentials):
        await AuthService(repo).login(LoginRequest(email="ann@example.com", password="secret1"))


async def test_logout_blacklists_token(repo):
    redis = AsyncMock()
    token = create_access_token("user-1")

    await AuthService(repo).logout(token, redis)

    jti, ttl = redis.blacklist.await_args.args
    assert jti
    assert ttl > 0
