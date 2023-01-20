from typing import Any

from db import database, engine, metadata
from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from posts import api_posts
from starlette.exceptions import HTTPException as StarletteHTTPException
from users import api_auth, api_users

app = FastAPI()
app.state.database = database
metadata.create_all(engine)


@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Any, exc: Any) -> JSONResponse:
    return JSONResponse({"detail": f"{exc.detail}"}, exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Any, exc: Any) -> JSONResponse:
    message = ""
    for pydantic_error in exc.errors():
        loc, msg = pydantic_error["loc"], pydantic_error["msg"]
        filtered_loc = loc[1:] if loc[0] in ("body", "query", "path") else loc
        field_string = ".".join(filtered_loc)
        message += f"\n{field_string} - {msg}"
    return JSONResponse(
        {"detail": "Invalid request", "errors": message},
        status.HTTP_422_UNPROCESSABLE_ENTITY
    )


app.include_router(api_auth.router, prefix="/api")
app.include_router(api_users.router, prefix="/api")
app.include_router(api_posts.router, prefix="/api")
