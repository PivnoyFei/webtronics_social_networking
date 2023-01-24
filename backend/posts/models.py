from typing import Any

import sqlalchemy as sa
from asyncpg import Record
from asyncpg.exceptions import ForeignKeyViolationError, UniqueViolationError
from db import Base, metadata
from posts.schemas import PostCreate
from redis import Redis
from settings import NOT_FOUND, REDIS_URL
from sqlalchemy.sql import func

db_redis = Redis.from_url(REDIS_URL, decode_responses=True)

posts = sa.Table(
    "posts", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("text", sa.Text),
    sa.Column("author", sa.Integer, sa.ForeignKey("users.id", ondelete='CASCADE')),
    sa.Column("timestamp", sa.DateTime(timezone=True), default=func.now()),
    sa.Column("update_date", sa.DateTime(timezone=True), default=None, onupdate=func.now()),
)
likes = sa.Table(
    "likes", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete='CASCADE')),
    sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id", ondelete='CASCADE')),
    sa.UniqueConstraint('user_id', 'post_id', name='unique_for_like')
)
dislikes = sa.Table(
    "dislikes", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete='CASCADE')),
    sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id", ondelete='CASCADE')),
    sa.UniqueConstraint('user_id', 'post_id', name='unique_for_dislikes')
)


class Post(Base):
    async def create(self, post_items: dict) -> Record:
        return await self.database.fetch_one(
            sa.insert(posts).values(post_items).returning(posts)
        )

    async def posts_count(self, author: int | None = None) -> Record:
        query = sa.select(func.count(posts.c.id).label("is_count"))
        if author:
            query = query.where(posts.c.author == author)
        return await self.database.fetch_one(query)

    async def posts_all(
        self,
        page: int = 1,
        limit: int = 6,
        author: int | None = None
    ) -> list[Record]:

        query = (
            sa.select(
                posts,
                func.count(likes.c.user_id).label("like"),
                func.count(dislikes.c.user_id).label("dislike")
            )
            .join(likes, likes.c.post_id == posts.c.id, full=True)
            .join(dislikes, dislikes.c.post_id == posts.c.id, full=True)
            .limit(limit)
            .offset((page - 1) * limit)
            .group_by(posts.c.id)
            .order_by(posts.c.timestamp.desc())
        )
        if author:
            query = query.where(posts.c.author == author)
        return await self.database.fetch_all(query)

    async def post_by_id(self, post_id: int) -> Record | None:
        return await self.database.fetch_one(
            sa.select(posts).where(posts.c.id == post_id)
        )

    async def author_by_id(self, post_id: int) -> Record | None:
        return await self.database.fetch_one(
            sa.select(posts.c.author).where(posts.c.id == post_id)
        )

    async def update(self, post_id: int, user_id: int, post_items: PostCreate) -> Record | None:
        return await self.database.fetch_one(
            sa.update(posts)
            .where(posts.c.id == post_id, posts.c.author == user_id)
            .values(text=post_items.text)
            .returning(posts)
        )

    async def delete(self, post_id: int, user_id: int) -> Record | None:
        query = await self.database.execute(
            sa.delete(posts)
            .where(posts.c.id == post_id, posts.c.author == user_id)
            .returning(posts.c.id)
        )
        return True if query else False


class LikeDislike(Base):
    async def count(self, post_id: int) -> Record:
        """ Counts the number of likes and dislikes. """
        return await self.database.fetch_one(
            sa.select(
                func.count(likes.c.user_id).label("like"),
                func.count(dislikes.c.user_id).label("dislike")
            )
            .join(likes, likes.c.post_id == posts.c.id, full=True)
            .join(dislikes, dislikes.c.post_id == posts.c.id, full=True)
            .where(posts.c.id == post_id)
            .group_by(posts.c.id)
        )

    async def _delete(self, post_id: int, user_id: int, model: Any) -> Any:
        """ Gets the likes or dislikes model and removes what is needed. """
        return await self.database.execute(
            sa.delete(model).where(model.c.post_id == post_id, model.c.user_id == user_id)
        )

    async def _create(self, post_id: int, user_id: int, model: Any) -> Any:
        """ Gets the likes or dislikes model and creates what is needed. """
        return await self.database.execute(
            sa.insert(model).values(post_id=post_id, user_id=user_id)
        )

    async def like(self, post_id: int, user_id: int, like: bool = False) -> Any:
        """
        The input receives a bool value like this or not.
        If like, creates like and removes dislikes.
        If like is already there, just delete it.
        """
        model_one, model_two = dislikes, likes
        if like:
            model_one, model_two = likes, dislikes
        try:
            await self._create(post_id, user_id, model_one)
        except UniqueViolationError:
            await self._delete(post_id, user_id, model_one)
        except ForeignKeyViolationError:
            return NOT_FOUND
        else:
            await self._delete(post_id, user_id, model_two)

        record = dict(await self.count(post_id))
        db_redis.hmset(f"id={post_id}", record)
        return record
