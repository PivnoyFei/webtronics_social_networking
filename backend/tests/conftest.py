from typing import Any, Generator

import pytest
import sqlalchemy
from db import metadata
from fastapi.testclient import TestClient
from main import app
from settings import DATABASE_URL, HOST


@pytest.fixture(autouse=True, scope="session")
def create_test_database() -> Generator:
    """ We create tables. """
    engine = sqlalchemy.create_engine(DATABASE_URL)
    metadata.create_all(engine)
    yield
    metadata.drop_all(engine)


@pytest.fixture()
def client() -> Generator:
    """ We connect to the database. """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def host(mocker: Any) -> Any:
    """ Set request.client.host. """
    mock_client = mocker.patch("fastapi.Request.client")
    mock_client.host = HOST
    return mock_client


@pytest.fixture
def user_one() -> dict:
    return {
        "username": "fakefive",
        "first_name": "fakefive",
        "last_name": "fakefive",
        "email": "fakefive@fake.fake",
        "password": "fakefive",
    }


@pytest.fixture
def user_other() -> dict:
    return {
        "username": "fakeother",
        "first_name": "fakeother",
        "last_name": "fakeother",
        "email": "fakeother@fake.fake",
        "password": "fakeother",
    }


@pytest.fixture
def user_validator() -> dict:
    return {
        "username": "fake_error",
        "first_name": "fake_error",
        "last_name": "fake_error",
        "email": "fake_error@fake.fake",
        "password": "fake_error",
    }


@pytest.fixture
def email_exists() -> dict:
    return {
        "username": "unique",
        "first_name": "unique",
        "last_name": "unique",
        "email": "fakeother@fake.fake",
        "password": "unique",
    }


@pytest.fixture
def username_exists() -> dict:
    return {
        "username": "fakeother",
        "first_name": "unique",
        "last_name": "unique",
        "email": "unique@fake.fake",
        "password": "unique",
    }
