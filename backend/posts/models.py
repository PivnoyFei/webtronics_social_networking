from typing import Any
from asyncpg.exceptions import UniqueViolationError
import sqlalchemy as sa
from asyncpg import Record
from db import Base, metadata
from posts.schemas import PostCreate
from sqlalchemy.sql import func

posts = sa.Table(
    "posts", metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("text", sa.Text),
    # sq.Column("image", sa.String(255), unique=True),
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

    async def posts_all(self) -> list[Record] | None:
        return await self.database.fetch_all(sa.select(posts))

    async def post_by_id(self, post_id: int) -> Record | None:
        return await self.database.fetch_one(
            sa.select(
                posts,
                func.count(likes.c.user_id).label("like"),
                func.count(dislikes.c.user_id).label("dislike")
            )
            .join(likes, likes.c.post_id == posts.c.id, full=True)
            .join(dislikes, dislikes.c.post_id == posts.c.id, full=True)
            .where(posts.c.id == post_id)
            .group_by(posts.c.id)
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
    async def count(self, post_id: int) -> dict[int, int]:
        """ Counts the number of likes and dislikes, returns a dictionary. """
        count_likes = await self.database.fetch_one(
            sa.select(func.count(likes.c.user_id).label("like"))
            .where(likes.c.post_id == post_id)
        )
        count_dislikes = await self.database.fetch_one(
            sa.select(func.count(dislikes.c.user_id).label("dislike"))
            .where(dislikes.c.post_id == post_id)
        )
        return {"like": int(count_likes.like), "dislike": int(count_dislikes.dislike)}

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

    async def like(self, post_id: int, user_id: int, like: bool = False) -> dict[int, int]:
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
        else:
            await self._delete(post_id, user_id, model_two)
        return await self.count(post_id)