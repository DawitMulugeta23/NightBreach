from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.config import get_settings
from app.core.error_handlers import register_error_handlers


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

register_error_handlers(app)

app.include_router(
    api_v1_router,
    prefix=settings.api_prefix,
)
