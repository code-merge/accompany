from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.models.base import Base

class Language(Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(Text, unique=True)
    label: Mapped[str] = mapped_column(Text)
