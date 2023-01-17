from datetime import datetime

from pydantic import BaseModel


class PostBase(BaseModel):
    id: int
    text: str
    # image: str
    author: int
    timestamp: datetime
    update_date: datetime | None = None


class PostCreate(BaseModel):
    text: str
    # image: str | None
