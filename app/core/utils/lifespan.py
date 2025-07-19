from contextlib import asynccontextmanager
from setup.compiler import compile_tailwind
from app.core.i18n import compile_all_translations

@asynccontextmanager
async def app_lifespan(app):
    """
    Asynchronous context manager for managing the application's lifespan.

    This function performs the following tasks during the application's lifespan:
    1. Compiles all translation files at startup by calling `compile_all_translations()`.
    2. Starts the Tailwind CSS compiler by calling `compile_tailwind()` and ensures it is terminated gracefully on shutdown.

    Args:
        app: The application instance.

    Yields:
        None. Used for managing setup and teardown logic.

    Exceptions:
        Any exceptions raised during compiler termination are caught and ignored to ensure graceful shutdown.
    """
    compile_all_translations()

    compiler = None
    try:
        compiler = compile_tailwind()
        yield
    finally:
        if compiler:
            try:
                compiler.terminate()
            except Exception:
                pass  # Gracefully ignore compiler shutdown errors
