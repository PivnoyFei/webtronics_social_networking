from asyncpg import Record
from db import Base, metadata
from sqlalchemy import Column, DateTime, Integer, String, Table, insert, select
from sqlalchemy.sql import func
from users.schemas import UserCreate

users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(255), unique=True, index=True),
    Column("password", String(255)),
    Column("username", String(150), unique=True, index=True),
    Column("first_name", String(150)),
    Column("last_name", String(150)),
    Column("timestamp", DateTime(timezone=True), default=func.now()),
)


class User(Base):
    async def user_by_id(self, pk: int) -> Record:
        return await self.database.fetch_one(
            select(users).where(users.c.id == pk)
        )

    async def user_by_username(self, username: str) -> Record:
        return await self.database.fetch_one(
            select(users).where(users.c.username == username)
        )

    async def check_by_email(self, email: str) -> Record | None:
        return await self.database.fetch_one(
            select(users.c.id).where(users.c.email == email)
        )

    async def check_by_username(self, username: str) -> Record | None:
        return await self.database.fetch_one(
            select(users.c.id).where(users.c.username == username)
        )

    async def id_password_by_username(self, username: str) -> Record | None:
        query = await self.database.fetch_one(
            select(users.c.id, users.c.password)
            .where(users.c.username == username)
        )
        return query

    async def create(self, user: UserCreate) -> int:
        return await self.database.execute(
            insert(users).values(
                email=user.email,
                password=user.password,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
            ).returning(users.c.id)
        )

    async def update_password(self, password: str, user_id: int) -> Record | None:
        return await self.database.execute(
            users.update()
            .where(users.c.id == user_id)
            .values(password=password)
            .returning(users.c.id)
        )
