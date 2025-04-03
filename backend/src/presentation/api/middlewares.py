import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from src.settings import config

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        logger.debug(
            f"Request: {request.method} {request.url.path} | "
            f"Response: {response.status_code} | "
            f"Time: {process_time:.4f}s"
        )
        return response


def setup_middlewares(app) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)