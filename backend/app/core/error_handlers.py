from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import NightBreachError


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(NightBreachError)
    async def handle_nightbreach_error(
        request: Request,
        exc: NightBreachError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )
