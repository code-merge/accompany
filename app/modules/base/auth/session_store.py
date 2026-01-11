from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from app.core.db.models import AuthSession

SESSION_HOURS = 1

async def create_login_session(db: AsyncSession, user_id: int) -> str:
    sid = str(uuid4())
    now = datetime.now(timezone.utc)
    session = AuthSession(
        id=sid,
        user_id=user_id,
        created_at=now,
        expires_at=now + timedelta(hours=SESSION_HOURS)
    )
    db.add(session)
    await db.commit()
    return sid

async def get_user_by_session(db: AsyncSession, session_id: str):
    result = await db.execute(
        select(AuthSession).where(AuthSession.id == session_id)
    )
    auth_sess = result.scalar_one_or_none()
    if auth_sess and auth_sess.expires_at > datetime.now(timezone.utc):
        return auth_sess.user
    return None

async def destroy_session(db: AsyncSession, session_id: str) -> None:
    await db.execute(delete(AuthSession).where(AuthSession.id == session_id))
    await db.commit()
