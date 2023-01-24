from typing import Any

from db import database
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from posts.models import LikeDislike, Post
from posts.schemas import PostBase, PostCreate, PostDetail, PostLike, PostList
from posts.utils import check_author, query_list
from redis import Redis
from settings import NOT_FOUND, REDIS_URL
from starlette.requests import Request
from users.schemas import UserOut
from users.utils import get_current_user

router = APIRouter(prefix='/posts', tags=["posts"])
db_post = Post(database)
db_like = LikeDislike(database)
db_redis = Redis.from_url(REDIS_URL, decode_responses=True)
PROTECTED = Depends(get_current_user)


@router.get("/", response_model=PostList, status_code=status.HTTP_200_OK)
async def get_posts(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(6, ge=1),
    author: int | None = Query(None)
) -> dict:
    """
    Viewing all posts is available to everyone.
    Implemented pagination and filtering by author.
    """
    query = await db_post.posts_all(page, limit, author)
    count = await db_post.posts_count(author)
    return await query_list(query, request, count[0], page, limit)


@router.post("/create", response_model=PostBase, status_code=status.HTTP_201_CREATED)
async def create_post(post_items: PostCreate, user: UserOut = PROTECTED) -> PostBase:
    """ Only registered users can post. """
    post_dict = dict(post_items)
    post_dict["author"] = user.id
    return await db_post.create(post_dict)


@router.get("/{post_id}", response_model=PostDetail, status_code=status.HTTP_200_OK)
async def get_post(post_id: int) -> Any:
    """ The post is available to everyone. """
    query = await db_post.post_by_id(post_id)
    if not query:
        return NOT_FOUND
    query_dict = dict(query)
    like_redis = db_redis.hgetall(f"id={post_id}")

    if not like_redis:
        like_redis = dict(await db_like.count(post_id))
        db_redis.hmset(f"id={post_id}", like_redis)

    query_dict.update(like_redis)
    return query_dict


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


@router.post("/{post_id}/like", response_model=PostLike, status_code=status.HTTP_200_OK)
async def like(post_id: int, user: UserOut = PROTECTED) -> Any:
    """
    When creating a like, it removes the dislike,
    if there is a like, it simply removes the like.
    """
    return await check_author(post_id, user.id, True)


@router.post("/{post_id}/dislike", response_model=PostLike, status_code=status.HTTP_200_OK)
async def dislike(post_id: int, user: UserOut = PROTECTED) -> Any:
    """ Does the same as the like function, only with dislikes. """
    return await check_author(post_id, user.id, False)
