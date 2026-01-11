from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db.models.base import Base

# Optional: for type hints only, not used at runtime
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.core.db.models.auth_session import AuthSession

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(Text, unique=True)
    hashed_password: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(Text, default="user")

    sessions: Mapped[list["AuthSession"]] = relationship(
        "AuthSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
