from sqlalchemy import Integer, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.models.base import Base

class Module(Base):
    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
