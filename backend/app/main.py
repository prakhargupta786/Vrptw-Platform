from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppError, app_error_handler


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version="0.1.0", openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
                  docs_url="/docs")
    app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, allow_credentials=True,
                       allow_methods=["*"], allow_headers=["*"])
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)
    return app


app = create_app()
