from typing import Any
from pathlib import Path
from functools import cached_property
from fastapi.responses import HTMLResponse
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings configuration class for the application.

    Attributes:
        APP_DIR (Path): The root directory of the application.
        CORE_DIR (Path): The core directory within the application.
        MODULES_DIR (Path): The directory containing all modules.
        DATA_DIR (Path): The directory for application data.
        ENABLED_MODULES (list[str]): List of enabled modules for static files.
        POSTGRES_SUPERUSER (str): PostgreSQL superuser name.
        POSTGRES_PASSWORD (str): PostgreSQL superuser password.
        POSTGRES_HOST (str): Host address for PostgreSQL.
        POSTGRES_PORT (int): Port number for PostgreSQL.
        FASTAPI_PROPERTIES (dict): Default properties for FastAPI app.
        DISABLE_DOCS (bool): Flag to disable FastAPI documentation endpoints.

    Properties:
        STATIC_DIRS (list[Path]): List of static directories, including core and enabled modules.
        TEMPLATE_DIRS (list[Path]): List of template directories, including core and enabled modules.
        MODULE_DATA_DIRS (list[Path]): List of data directories for each enabled module.
        CORE_DATA_DIR (Path): Data directory for the core module.
        fastapi_kwargs (dict[str, Any]): FastAPI keyword arguments, including documentation settings.
    """

    APP_DIR: Path = Path(__file__).resolve().parents[2]
    CORE_DIR: Path = APP_DIR / "core"
    MODULES_DIR: Path = APP_DIR / "modules"
    DATA_DIR: Path = APP_DIR / "data"

    ENABLED_MODULES: list[str] = ["onboarding"]  # Add the modules you want to enable for static files. here
    
    POSTGRES_SUPERUSER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432

    @property
    def STATIC_DIRS(self) -> list[Path]:
        return [self.APP_DIR / "static"] + [
            self.MODULES_DIR / mod / "static" for mod in self.ENABLED_MODULES
        ]

    # @property
    @cached_property
    def TEMPLATE_DIRS(self) -> list[Path]:
        base = [
            self.APP_DIR / "core" / "ui" / "templates",
            self.APP_DIR / "core" / "ui",
            self.APP_DIR / "core" / "ui" / "components"
        ]
        module_dirs = []
        for mod in self.ENABLED_MODULES:
            module_base = self.MODULES_DIR / mod / "ui"
            module_dirs.append(module_base / "templates")  # for welcome.html, etc.
            module_dirs.append(module_base)                # for components/
        return base + module_dirs

    @property
    def MODULE_DATA_DIRS(self) -> list[Path]:
        return [self.MODULES_DIR / mod / "data" for mod in self.ENABLED_MODULES]

    @property
    def CORE_DATA_DIR(self) -> Path:
        return self.CORE_DIR / "data"


    FASTAPI_PROPERTIES: dict = {
        "title": "Accompany",
        "description": "Your business companion",
        "version": "0.0.1",
        "default_response_class": HTMLResponse,
    }

    DISABLE_DOCS: bool = True # Set True to disable /docs and redoc endpoints in production

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        kwargs = self.FASTAPI_PROPERTIES.copy()
        if self.DISABLE_DOCS:
            kwargs.update(
                {
                    "openapi_url": None,
                    "docs_url": None,
                    "redoc_url": None,
                }
            )
        return kwargs


settings = Settings()
