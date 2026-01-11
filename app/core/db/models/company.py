from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db.models.base import Base

class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    industry: Mapped[str] = mapped_column(Text)
