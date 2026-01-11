from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.hash import bcrypt
from app.core.db.models import User

async def validate_credentials(
    db: AsyncSession,
    email: str,
    password: str
) -> User | None:
    """
    Verifies email + password. Returns User if valid, else None.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user and bcrypt.verify(password, user.hashed_password):
        return user
    return None
