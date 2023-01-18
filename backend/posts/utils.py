from db import database
from posts.models import Post
from starlette.requests import Request

db_post = Post(database)


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
