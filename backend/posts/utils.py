from typing import Any

from db import database
from fastapi import status
from fastapi.responses import JSONResponse
from posts.models import LikeDislike, Post
from settings import NOT_FOUND
from starlette.requests import Request

db_post = Post(database)
db_like = LikeDislike(database)


async def query_list(query: list, request: Request, count: int, page: int, limit: int) -> dict:
    """
    Composes a json response for the user in accordance with the requirements.
    Composes the next, previous, and number of pages to paginate.
    """
    next_page = (
        str(request.url).replace(f"page={page}", f"page={page + 1}")
        if page and page * limit < count else None
    )
    previous = (
        str(request.url).replace(f"page={page}", f"page={page - 1}")
        if page and page > 1 else None
    )
    return {
        "count": count,
        "next": next_page,
        "previous": previous,
        "results": query
    }


async def check_author(post_id: int, user_id: int, like: bool) -> Any:
    author = await db_post.author_by_id(post_id)
    if not author:
        return NOT_FOUND
    if author.author == user_id:
        return JSONResponse(
            {"detail": "Just not your post"},
            status.HTTP_403_FORBIDDEN,
        )
    return await db_like.like(post_id, user_id, like)
