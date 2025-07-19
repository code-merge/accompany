from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.core.config.config import settings
from app.core.utils.lifespan import app_lifespan
from app.core.utils.static_mounts import mount_static_dirs

def get_app() -> FastAPI:
    """
    Creates and configures the FastAPI application instance with custom settings, middleware, and routing.

    Configuration Workflow:
    -----------------------
    1. Initializes the FastAPI app using a custom lifespan handler (`app_lifespan`) and additional kwargs from `settings.fastapi_kwargs`.
    2. Mounts static directories via `mount_static_dirs()` to serve frontend assets.
    3. Adds session middleware using Starlette's `SessionMiddleware` with the specified secret key.
    4. Registers the onboarding router under the `/onboarding` prefix with the tag "onboarding".

    Returns:
    --------
    FastAPI
        A fully configured FastAPI app instance, ready to serve requests.

    Notes:
    ------
    - The returned app instance is assigned to the module-level `app` variable for ASGI compatibility.
    - Designed for modular extension, additional routers or middleware can be added within this function.
    """
    
    app = FastAPI(lifespan=app_lifespan, **settings.fastapi_kwargs)

    mount_static_dirs(app)

    app.add_middleware(SessionMiddleware, secret_key="<YOUR SECRET KEY>")


    return app



app = get_app()
"""
Module-level application instance used by ASGI servers (e.g., uvicorn) to serve the FastAPI app.

This exposes the configured app so it can be referenced as an entry point in deployment setups or test clients.
"""