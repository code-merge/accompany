from fastapi import Request, Depends, HTTPException
from starlette.status import HTTP_403_FORBIDDEN
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.dependency import get_db
from app.modules.base.auth.session_store import get_user_by_session

async def require_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    FastAPI dependency. Ensures a valid session cookie exists.
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    user = await get_user_by_session(db, session_id)
    if not user:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN)
    return user
