from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class AuthTokenMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token_cookie = request.cookies.get("access_token", None)
        if token_cookie:
            request.state.access_token = (
                token_cookie  # Użyj stanu żądania do przechowywania tokena
            )
        response = await call_next(request)
        return response
