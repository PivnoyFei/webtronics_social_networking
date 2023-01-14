from db import database
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from users.models import User
from users.schemas import UserCreate, UserOut
from users.utils import get_current_user, get_hashed_password

router = APIRouter(prefix='/users', tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", scheme_name="JWT")
db_user = User(database)


@router.post("/signup", response_model=UserOut)
async def create_user(user: UserCreate) -> JSONResponse | UserOut:
    if await db_user.check_by_email(user.email):
        return JSONResponse(
            {"message": "Email already exists"},
            status.HTTP_400_BAD_REQUEST,
        )
    if await db_user.user_by_username(user.username):
        return JSONResponse(
            {"message": "Username already exists"},
            status.HTTP_400_BAD_REQUEST,
        )
    user.password = await get_hashed_password(user.password)
    return await db_user.user_by_id(await db_user.create(user))


@router.get('/me', response_model=UserOut)
async def get_me(user: UserOut = Depends(get_current_user)) -> UserOut:
    """ Get details of currently logged in user. """
    return user
