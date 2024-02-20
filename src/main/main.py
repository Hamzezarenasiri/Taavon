from src.babel import babel
import os

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.apps.api import home_router
from src.apps.api.v1.router import router_v1
from src.core.base.schema import ErrorResponse
from src.core.common.exceptions import CustomHTTPException
from src.fastapi_babel import _
from src.main.config import api_settings, app_settings
from src.main.events import (
    create_start_app_handler,
    create_stop_app_handler,
    lifespan,
)


import sentry_sdk

sentry_sdk.init(
    dsn="https://8dcf2f288a42650b655fc844790d06be@o1178736.ingest.sentry.io/4505946411302912",
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)


def create_application() -> FastAPI:
    application = FastAPI(
        title=app_settings.PROJECT_NAME,
        description=app_settings.PROJECT_DESCRIPTION,
        debug=app_settings.DEBUG,
        servers=app_settings.PROJECT_SERVERS,
        responses={422: {"model": ErrorResponse}},
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in api_settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=api_settings.BACKEND_CORS_METHODS,
        allow_headers=api_settings.BACKEND_CORS_HEADERS,
    )

    application.add_event_handler("startup", create_start_app_handler())
    application.add_event_handler("shutdown", create_stop_app_handler())
    application.include_router(router_v1, prefix=api_settings.API_V1_STR)
    if not os.path.exists(app_settings.DEFAULT_MEDIA_PATH):
        os.makedirs(app_settings.DEFAULT_MEDIA_PATH)
    application.mount(
        "/media",
        StaticFiles(directory=app_settings.DEFAULT_MEDIA_PATH),
        name="media",
    )
    return application


app = create_application()
babel.init_app(app)


@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(_: Request, exc: HTTPException):
    body = jsonable_encoder(exc)
    body.pop("status_code")
    body.pop("headers")
    return JSONResponse(content=body, status_code=exc.status_code, headers=exc.headers)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    exc = CustomHTTPException(
        status_code=exc.status_code, detail=exc.detail, headers=exc.headers
    )
    return await custom_http_exception_handler(request, exc)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc = CustomHTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=exc.errors(),
        message=_("Data validation error occurred."),
    )
    return await custom_http_exception_handler(request, exc)


app.responses = {422: {"model": ErrorResponse}}

if __name__ == "__main__":
    # pragma: no cover
    uvicorn.run(
        app,
        host=app_settings.SERVER_HOST,
        port=app_settings.SERVER_PORT,
        reload=app_settings.APP_RELOAD,
        loop="none",
    )
