from datetime import datetime, timedelta

from asyncpg import Record
from db import Base, metadata
from settings import REFRESH_TOKEN_EXPIRE_MINUTES
from sqlalchemy import (Column, DateTime, ForeignKey, Integer, String, Table,
                        insert, select)
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
auth_token = Table(
    "auth_token", metadata,
    Column("id", Integer, primary_key=True),
    Column("ip", String(45), index=True),
    Column("refresh_token", String, index=True),
    Column("created", DateTime),
    Column("user_id", Integer, ForeignKey("users.id", ondelete='CASCADE')),
)


class Token(Base):
    async def create_token(self, ip: str, user_id: int, refresh_token: str) -> int:
        return await self.database.execute(
            insert(auth_token).values(
                ip=ip,
                refresh_token=refresh_token,
                created=datetime.now() + timedelta(weeks=REFRESH_TOKEN_EXPIRE_MINUTES),
                user_id=user_id,
            )
        )

    async def check_token(self, ip: str, user_id: int, refresh_token: str) -> Record | None:
        """ Returns information about the owner of the specified token. """
        return await self.database.fetch_one(
            select(auth_token.c.user_id)
            .where(
                auth_token.c.ip == ip,
                auth_token.c.user_id == user_id,
                auth_token.c.refresh_token == refresh_token,
                auth_token.c.created > datetime.now()
            )
        )

    async def count_token_user(self, user_id: int) -> Record:
        return await self.database.fetch_one(
            select(
                func.count(auth_token.c.refresh_token).label("token"),
            )
            .where(auth_token.c.user_id == user_id)
            .group_by(auth_token.c.user_id)
        )

    async def update_token(self, ip: str, user_id: int, token: str) -> None:
        await self.database.fetch_one(
            auth_token.update()
            .where(
                auth_token.c.ip == ip,
                auth_token.c.user_id == user_id,
                auth_token.c.refresh_token == token
            )
            .values(refresh_token=token)
        )

    async def delete_by_id(self, user_id: int) -> None:
        await self.database.execute(
            auth_token.delete().where(auth_token.c.user_id == user_id)
        )

    async def delete_by_ip_token(self, ip: str, user_id: int, token: str) -> None:
        await self.database.execute(
            auth_token.delete()
            .where(auth_token.c.ip == ip, auth_token.c.refresh_token == token)
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
