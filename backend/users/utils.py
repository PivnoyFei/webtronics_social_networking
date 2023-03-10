from datetime import datetime, timedelta
from typing import Any

import settings
from db import database
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.hash import bcrypt
from pydantic import ValidationError
from redis import Redis
from settings import REDIS_URL
from users.models import User
from users.schemas import TokenPayload

db_user = User(database)
db_redis = Redis.from_url(REDIS_URL, decode_responses=True)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token/login",
    scheme_name="JWT"
)


async def get_hashed_password(password: str) -> str:
    """ Hashes the user's password. """
    return bcrypt.hash(password)


async def verify_password(password: str, hashed_pass: str) -> bool:
    """ Validates a hashed user password. """
    return bcrypt.verify(password, hashed_pass)


async def _get_token(sub: int, secret: str, expire_minutes: int) -> str:
    """ Called from create_access_token and create_refresh_token. """
    exp = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode = {"exp": exp, "sub": str(sub)}
    encoded_jwt = jwt.encode(to_encode, secret, settings.ALGORITHM)
    return encoded_jwt


async def create_access_token(sub: int) -> str:
    """ Creates a access token. """
    return await _get_token(
        sub,
        settings.JWT_SECRET_KEY,
        settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


async def create_refresh_token(sub: int) -> str:
    """ Creates a refresh token. """
    return await _get_token(
        sub,
        settings.JWT_REFRESH_SECRET_KEY,
        settings.REFRESH_TOKEN_EXPIRE_MINUTES,
    )


async def check_token(token: str, secret: str, refresh_host: str = '') -> Any:
    """
    Checks the token time.
    if refresh_token checks if the IP address exists in the database.
    if not, removes all tokens
    """
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    try:
        payload = jwt.decode(
            token, secret, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise exception
        if refresh_host:
            if db_redis.hmget(f"user={token_data.sub}", refresh_host)[0] == token:
                return token_data.sub
            db_redis.hdel(f"user={token_data.sub}", refresh_host)
            raise exception

    except (JWTError, ValidationError):
        raise exception

    user = await db_user.user_by_id(token_data.sub)
    if not user:
        raise exception
    return user


async def redis_count_token_and_save(user_id: int, host: str) -> dict[str, str]:
    access_token = await create_access_token(user_id)
    refresh_token = await create_refresh_token(user_id)

    if len(db_redis.hgetall(f"user={user_id}")) > 10:
        db_redis.delete(f"user={user_id}")
    db_redis.hmset(f"user={user_id}", {host: refresh_token})

    return {"access_token": access_token, "refresh_token": refresh_token}


async def get_current_user(token: str = Depends(oauth2_scheme)) -> type:
    """?????????????????? ???????????????? ?????????????????????????????????? ????????????????????????."""
    return await check_token(token, settings.JWT_SECRET_KEY)
