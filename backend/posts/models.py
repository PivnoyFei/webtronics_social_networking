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
