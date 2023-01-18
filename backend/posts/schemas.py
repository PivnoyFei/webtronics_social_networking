from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    id: int
    text: str
    author: int
    timestamp: datetime
    update_date: datetime | None = None


class PostCreate(BaseModel):
    text: str


class PostLike(BaseModel):
    like: int
    dislike: int


class PostDetail(PostLike, PostBase):
    pass


class PostList(BaseModel):
    count: int
    next: str | None = None
    previous: str | None = None
    results: list[PostDetail] = []
