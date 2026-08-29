from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


def _error_payload(code: str, message: str, details=None) -> dict:
    payload = {"error": {"code": code, "message": message}}
    if details:
        payload["error"]["details"] = details
    return payload


def _cors_headers(request: Request) -> dict:
    # FastAPI exception handlers bypass CORSMiddleware, so we must attach
    # the Allow-Origin header manually. Without it the browser blocks the
    # error response and shows a misleading "network error" instead of the
    # actual HTTP status code.
    origin = request.headers.get("origin")
    if not origin:
        return {}
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning("AppError %s on %s: %s", exc.code, request.url.path, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message),
            headers=_cors_headers(request),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = []
        for err in exc.errors():
            location = ".".join(str(part) for part in err.get("loc", []) if part != "body")
            details.append({"field": location or "body", "issue": err.get("msg", "invalid value")})
        return JSONResponse(
            status_code=422,
            content=_error_payload("validation_error", "Some provided values are invalid.", details),
            headers=_cors_headers(request),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content=_error_payload("internal_error", "An unexpected error occurred. Please try again."),
            headers=_cors_headers(request),
        )
