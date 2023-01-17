import dataclasses
from typing import Any

from fastapi import status


@dataclasses.dataclass
class Cache:
    headers = {"authorization": "Bearer"}
    user_one = {}
    user_other = {}
    refresh_token = {"refresh_token": ""}


def test_post_user_create(client: Any, user_one: dict, user_other: dict) -> None:
    for user in (user_one, user_other):
        response = client.post("/api/users/signup", json=user)
        assert response.status_code == status.HTTP_201_CREATED
        assert len(response.json()) == 6
        assert user["email"] in response.json()["email"]
        Cache.user_one = response.json()


def test_post_user_create_with_error(
    client: Any, user_validator: dict, email_exists: dict, username_exists: dict
) -> None:
    response = client.post("/api/users/signup", json=user_validator)
    assert response.json() == {'detail': 'Unacceptable symbols'}
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = client.post("/api/users/signup", json=email_exists)
    assert response.json() == {'message': 'Email already exists'}
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = client.post("/api/users/signup", json=username_exists)
    assert response.json() == {'message': 'Username already exists'}
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_post_login_incorrect(client: Any, user_one: dict, host: Any) -> None:
    data = {"username": user_one["username"], "password": "incorrect"}
    response = client.post("/api/auth/token/login", data=data)
    assert response.json() == {"detail": "Incorrect password"}
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    data = {"username": "incorrect", "password": user_one["password"]}
    response = client.post("/api/auth/token/login", data=data)
    assert response.json() == {"detail": "Incorrect username"}
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_post_login(client: Any, user_one: dict, host: Any) -> None:
    data = {"username": user_one["username"], "password": user_one["password"]}
    response = client.post("/api/auth/token/login", data=data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()

    access_token = response.json()["access_token"]
    Cache.headers = {"authorization": f"Bearer {access_token}"}
    Cache.refresh_token = {"refresh_token": response.json()["refresh_token"]}


def test_post_me(client: Any, user_one: dict, host: Any) -> None:
    response = client.get("/api/users/me", headers=Cache.headers)
    assert response.status_code == status.HTTP_200_OK
    assert user_one["email"] in response.json()["email"]


def test_post_token_refresh(client: Any, host: Any) -> None:
    response = client.post("/api/auth/token/refresh", json=Cache.refresh_token)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_post_token_refresh_other_ip(client: Any, host: Any) -> None:
    host.host = "127.0.0.1"
    response = client.post("/api/auth/token/refresh", json=Cache.refresh_token)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid credentials'}
