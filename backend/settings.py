import os

from dotenv import load_dotenv
from fastapi import status
from fastapi.responses import JSONResponse

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 5
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

ALGORITHM = os.getenv("ALGORITHM", default="HS256")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", default="key")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY", default="key")

POSTGRES_DB = os.getenv("POSTGRES_DB", default="postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", default="postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", default="postgres")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", default="localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", default="5432")

REDIS_HOST = os.getenv("REDIS_HOST", default="localhost")
REDIS_PORT = os.getenv("REDIS_PORT", default="6379")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

TESTING = os.getenv("TESTING", default="False")
if TESTING == "True":
    POSTGRES_SERVER = "db-test"
DATABASE_URL = (f"postgresql://{POSTGRES_USER}:"
                f"{POSTGRES_PASSWORD}@"
                f"{POSTGRES_SERVER}:"
                f"{POSTGRES_PORT}/"
                f"{POSTGRES_DB}")

NOT_FOUND = JSONResponse({"detail": "NotFound"}, status.HTTP_404_NOT_FOUND)

""" For tests. """
HOST = "192.168.123.132"
