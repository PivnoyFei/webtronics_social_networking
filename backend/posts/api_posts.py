from typing import Any

from db import database
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from posts.models import Post
from posts.schemas import PostBase, PostCreate
from users.schemas import UserOut
from users.utils import get_current_user

router = APIRouter(prefix='/posts', tags=["posts"])
db_post = Post(database)
PROTECTED = Depends(get_current_user)


@router.get("/", response_model=list[PostBase], status_code=status.HTTP_200_OK)
async def get_posts() -> list | None:
    """ Viewing all posts is available to everyone. """
    return await db_post.posts_all()


@router.post("/create", response_model=PostBase, status_code=status.HTTP_201_CREATED)
async def create_post(post_items: PostCreate, user: UserOut = PROTECTED) -> PostBase:
    """ Only registered users can post. """
    post_dict = dict(post_items)
    post_dict["author"] = user.id
    return await db_post.create(post_dict)


@router.get("/{post_id}", response_model=PostBase, status_code=status.HTTP_200_OK)
async def get_post(post_id: int) -> Any:
    """ The post is available to everyone. """
    return await db_post.post_by_id(post_id)


@router.put("/{post_id}", response_model=PostBase, status_code=status.HTTP_200_OK)
async def update_post(post_id: int, post_items: PostCreate, user: UserOut = PROTECTED) -> Any:
    """ Posts can only be edited by the author. """
    post = await db_post.update(post_id, user.id, post_items)
    if not post:
        return JSONResponse(
            {"detail": "Only the author can edit or the post does not exist"},
            status.HTTP_403_FORBIDDEN,
        )
    return post


@router.delete("/{post_id}", status_code=status.HTTP_404_NOT_FOUND)
async def delete_post(post_id: int, user: UserOut = PROTECTED) -> Any:
    """ Posts can only be deleted by the author. """
    if not await db_post.delete(post_id, user.id):
        return JSONResponse(
            {"detail": "Only the author can delete or has already deleted"},
            status.HTTP_403_FORBIDDEN,
        )
    return JSONResponse({"detail": "Removed"}, status.HTTP_404_NOT_FOUND)
