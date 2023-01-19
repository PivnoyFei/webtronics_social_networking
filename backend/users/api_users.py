from db import database
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from settings import NOT_FOUND
from users.models import User
from users.schemas import SetPassword, UserCreate, UserOut, UserPassword
from users.utils import get_current_user, get_hashed_password, verify_password

router = APIRouter(prefix='/users', tags=["users"])
db_user = User(database)
PROTECTED = Depends(get_current_user)


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate) -> UserOut | JSONResponse:
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


@router.get('/me', response_model=UserOut, status_code=status.HTTP_200_OK)
async def get_me(user: UserOut = PROTECTED) -> UserOut:
    """ Get details of currently logged in user. """
    return user


@router.get("/{pk}", response_model=UserOut, status_code=status.HTTP_200_OK)
async def user_id(pk: int) -> UserOut | JSONResponse:
    """ User profile. Available to all users. """
    return await db_user.user_by_id(pk) or NOT_FOUND


@router.put("/set_password", status_code=status.HTTP_200_OK)
async def set_password(user_pas: SetPassword, user: UserPassword = PROTECTED) -> JSONResponse:
    if not await verify_password(user_pas.current_password, user.password):
        return JSONResponse(
            {"detail": "Incorrect password"}, status.HTTP_400_BAD_REQUEST
        )
    password_hashed = await get_hashed_password(user_pas.new_password)
    if not await db_user.update_password(password_hashed, user.id):
        return JSONResponse(
            {"detail": "Error"}, status.HTTP_401_UNAUTHORIZED
        )
    return JSONResponse(
        {"detail": "Changed"}, status.HTTP_200_OK
    )
