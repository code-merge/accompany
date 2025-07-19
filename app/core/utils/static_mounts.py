from fastapi.staticfiles import StaticFiles
from app.core.config.config import settings

def mount_static_dirs(app):
    """
    Mounts static directories to the given ASGI application.

    This function mounts the main static directory and a 'libs' directory to the app.
    It also iterates through additional static directories defined in `settings.STATIC_DIRS`
    and mounts them under `/static/{module_name}` if they exist and are directories.
    The module name is inferred from the directory structure. Invalid or non-existent
    directories are skipped gracefully.

    Args:
        app: The ASGI application instance to which static directories will be mounted.

    Raises:
        None. Any exceptions during mounting of module-level statics are caught and skipped.
    """
    # Mount core static + libs
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIRS[0]), name="static")
    app.mount("/libs", StaticFiles(directory=settings.APP_DIR / "libs"), name="libs")

    # Conditionally mount module-level statics
    for path in settings.STATIC_DIRS[1:]:
        if path.exists() and path.is_dir():
            module_name = (
                path.parts[-2] if path.parts[-1] == "static" else path.parts[-1]
            )
            try:
                app.mount(f"/static/{module_name}", StaticFiles(directory=path), name=f"{module_name}-static")
            except Exception:
                continue  # Fail-safe: skip invalid mounts gracefully
