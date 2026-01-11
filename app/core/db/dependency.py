# app/core/db/dependency.py

from typing import AsyncGenerator

from fastapi import HTTPException, Request
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.db.db_manager import get_db_admin_engine
from app.core.services.credentials import ensure_cred_paths, read_db_creds

# ─── Module‐level cache ───────────────────────────────────────────────────────
_cached_profile: str | None = None
_cached_mtime:     float  | None = None
_cached_factory:   async_sessionmaker[AsyncSession] | None = None


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Yields an AsyncSession built from the most recently created ~/.accompany/*.ini.
    Session factory is rebuilt only when a new profile file appears.
    """
    global _cached_profile, _cached_mtime, _cached_factory

    # 1) Locate cred files
    cred_dir, _ = ensure_cred_paths()
    ini_files = list(cred_dir.glob("*.ini"))
    if not ini_files:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No database credential profiles found"
        )

    # 2) Pick newest by mtime
    newest_file = max(ini_files, key=lambda p: p.stat().st_mtime)
    profile = newest_file.stem
    mtime   = newest_file.stat().st_mtime

    # 3) Rebuild factory only if profile or file‐time changed
    if (
        _cached_factory is None
        or profile      != _cached_profile
        or mtime        != _cached_mtime
    ):
        try:
            creds = read_db_creds(profile)
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed loading credentials for profile '{profile}': {e}"
            )

        # Use your existing db_manager to get an AsyncEngine
        engine = get_db_admin_engine(creds)

        # Build & cache the sessionmaker
        _cached_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        _cached_profile  = profile
        _cached_mtime    = mtime

    # 4) Yield an AsyncSession from the cached factory
    assert _cached_factory is not None  # for mypy/type‐checkers
    async with _cached_factory() as session:
        yield session
