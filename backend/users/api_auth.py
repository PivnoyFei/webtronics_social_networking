from typing import Any

from db import database
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm as OAuth2Form
from redis import Redis
from settings import JWT_REFRESH_SECRET_KEY, REDIS_URL
from starlette.requests import Request
from users import utils
from users.models import Token, User
from users.schemas import TokenBase, TokenSchema, UserOut

router = APIRouter(prefix='/auth', tags=["auth"])
db_redis = Redis.from_url(REDIS_URL, decode_responses=True)
db_user = User(database)
db_token = Token(database)


@router.post("/token/login", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login(request: Request, user: OAuth2Form = Depends()) -> Any:
    """ Authorization by username and password, issues a token. """
    user_cls = await db_user.id_password_by_username(user.username)
    if not user_cls:
        return JSONResponse(
            {"detail": "Incorrect username"},
            status.HTTP_400_BAD_REQUEST
        )
    if not await utils.verify_password(user.password, user_cls.password):
        return JSONResponse(
            {"detail": "Incorrect password"},
            status.HTTP_400_BAD_REQUEST
        )
    if request.client is not None:
        access_token = await utils.create_access_token(user_cls.id),
        refresh_token = await utils.create_refresh_token(user_cls.id)
        await db_token.create_token(request.client.host, user_cls.id, refresh_token)
        return {"access_token": access_token, "refresh_token": refresh_token}


@router.post('/token/refresh', response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def refresh_token(request: Request, token: TokenBase) -> Any:
    if request.client is not None:
        user_id = await utils.check_token(
            token.refresh_token, JWT_REFRESH_SECRET_KEY, request.client.host
        )
        if not user_id:
            return RedirectResponse('/api/auth/token/login', status.HTTP_302_FOUND)

        access_token = await utils.create_access_token(user_id),
        refresh_token = await utils.create_refresh_token(user_id)

        count_token = await db_token.count_token_user(user_id)
        if count_token.token > 10:
            await db_token.delete_by_id(user_id)
            await db_token.create_token(request.client.host, user_id, refresh_token)
        else:
            await db_token.update_token(request.client.host, user_id, refresh_token)
        return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/token/logout", status_code=status.HTTP_404_NOT_FOUND)
async def logout(user: UserOut = Depends(utils.get_current_user)) -> None:
    await db_token.delete_by_id(user.id)
