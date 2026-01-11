# app/core/auth/middleware/auth_guard.py

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, Response
from starlette.status import HTTP_303_SEE_OTHER

# Exact public paths (only what's explicitly defined is allowed)
PUBLIC_PATHS = {
    "/auth/login",
    "/auth/forget-password",
    "/robots.txt",
    "/favicon.ico",
}

# Folder-level public prefixes (allow all nested assets under these)
PUBLIC_PREFIXES = [
    "/static",
    "/libs",
    "/website",
    "/onboarding",
]

class AuthGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # ✅ Allow exact path matches
        if path in PUBLIC_PATHS:
            return await call_next(request)

        # ✅ Allow prefix matches (e.g., /libs/htmx.min.js)
        if any(path == prefix or path.startswith(prefix + "/") for prefix in PUBLIC_PREFIXES):
            return await call_next(request)

        # 🔐 Check session cookie
        sid = request.cookies.get("session_id")
        if not sid or not await self.is_valid_session(sid):
            response = Response(status_code=HTTP_303_SEE_OTHER)
            response.headers["Location"] = "/auth/login"
            return response

        return await call_next(request)

    async def is_valid_session(self, sid: str) -> bool:
        # 🧠 Swap this with your actual DB or cache-based session check
        return bool(sid and len(sid) == 36)  # UUID sanity check
