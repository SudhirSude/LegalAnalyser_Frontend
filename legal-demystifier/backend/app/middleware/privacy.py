from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("privacy_middleware")


class PrivacyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # remove or obfuscate sensitive headers before calling next
        # example: don't log request body
        response = await call_next(request)
        # also scrub response if needed (avoid logging full doc text)
        return response
