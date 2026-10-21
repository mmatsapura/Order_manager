from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from app.core.exceptions import EmailTaken, InvalidCredentials
from app.db.redis import RedisDB
from app.dependencies import get_user_repository, get_current_user, get_redis, bearer_token
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserPublic
from app.services.auth import AuthService
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.user import User


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate, repo: UserRepository = Depends(get_user_repository)):
    service = AuthService(repo)
    try:
        return await service.register(body)
    except EmailTaken:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Email already registered')


@router.post('/login', response_model=TokenResponse)
async def login(body: LoginRequest, repo: UserRepository = Depends(get_user_repository)):
    service = AuthService(repo)
    try:
        return await service.login(body)
    except InvalidCredentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')


@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
async def logout(credentials: (HTTPAuthorizationCredentials | None) = Depends(bearer_token), _current_user: User = Depends(get_current_user), redis: RedisDB = Depends(get_redis), repo: UserRepository = Depends(get_user_repository)) -> None:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Unauthorized')
    service = AuthService(repo)
    await service.logout(credentials.credentials, redis)
    return


@router.get('/me', response_model=UserPublic)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
