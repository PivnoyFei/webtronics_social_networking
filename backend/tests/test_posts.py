from typing import Any

from fastapi import status
from tests.conftest import Cache


def test_get_posts_none(client: Any, answer: dict) -> None:
    response = client.get("/api/posts/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == answer


def test_get_post_none(client: Any, post: list) -> None:
    response = client.get("/api/posts/1000")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_post_create_not_login(client: Any) -> None:
    json = {"text": "post_create"}
    response = client.post("/api/posts/create", json=json)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


def test_post_create(client: Any, post: list) -> None:
    headers = Cache.headers
    for i in post:
        response = client.post("/api/posts/create", json=i, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert i["text"] in response.json()["text"]
        Cache.post.append(response.json()["id"])


def test_get_post(client: Any, post: list) -> None:
    response = client.get(f"/api/posts/{Cache.post[0]}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == post[0]["text"]


def test_get_posts(client: Any, post: list) -> None:
    response = client.get("/api/posts/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == len(post)
    assert len(response.json()["results"]) == 6


def test_get_posts_page(client: Any, post: list) -> None:
    for page in range(1, 10):
        for limit in range(1, 5):
            response = client.get(f"/api/posts/?page={page}&limit={limit}")
            assert response.status_code == status.HTTP_200_OK
            assert len(response.json()["results"]) == limit
            post_index = post[-((page - 1) * limit) - 1]["text"]
            assert response.json()["results"][0]["text"] == post_index


def test_post_update_other_client(client: Any) -> None:
    json = {"text": "post_update"}
    response = client.put(
        f"/api/posts/{Cache.post[0]}", json=json, headers=Cache.headers_other
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "Only the author can edit or the post does not exist"
    }


def test_post_update(client: Any) -> None:
    json = {"text": "post_update"}
    response = client.put(
        f"/api/posts/{Cache.post[0]}", json=json, headers=Cache.headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["text"] == json["text"]


def test_post_delete_other_client(client: Any) -> None:
    response = client.delete(
        f"/api/posts/{Cache.post[0]}", headers=Cache.headers_other
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "detail": "Only the author can delete or has already deleted"
    }


def test_post_delete(client: Any) -> None:
    response = client.delete(
        f"/api/posts/{Cache.post[0]}", headers=Cache.headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Removed"}


def test_post_like_no_post(client: Any) -> None:
    response = client.post(
        f"/api/posts/{Cache.post[0]}/like", headers=Cache.headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "NotFound"}


def test_post_like_author(client: Any) -> None:
    response = client.post(
        f"/api/posts/{Cache.post[1]}/like", headers=Cache.headers
    )
    assert response.status_code == status.HTTP_418_IM_A_TEAPOT
    assert response.json() == {"detail": "Just not your post"}


def test_post_like(client: Any) -> None:
    response = client.post(
        f"/api/posts/{Cache.post[1]}/like", headers=Cache.headers_other
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'dislike': 0, 'like': 1}


def test_post_dislike_no_post(client: Any) -> None:
    response = client.post(
        f"/api/posts/{Cache.post[0]}/dislike", headers=Cache.headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "NotFound"}


def test_post_dislike_author(client: Any) -> None:
    response = client.post(
        f"/api/posts/{Cache.post[1]}/dislike", headers=Cache.headers
    )
    assert response.status_code == status.HTTP_418_IM_A_TEAPOT
    assert response.json() == {"detail": "Just not your post"}


def test_post_dislike(client: Any) -> None:
    response = client.post(
        f"/api/posts/{Cache.post[1]}/dislike", headers=Cache.headers_other
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'dislike': 1, 'like': 0}
