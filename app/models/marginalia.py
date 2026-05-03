from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class NoteType(str, enum.Enum):
    intuition = "intuition"
    definition = "definition"
    note = "note"
    question = "question"


class Marginalia(Base, TimestampMixin):
    __tablename__ = "marginalia"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    article_slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    section_id: Mapped[str | None] = mapped_column(String(255))
    note_type: Mapped[NoteType] = mapped_column(
        SAEnum(NoteType, name="notetype"), default=NoteType.note, nullable=False
    )
    label: Mapped[str | None] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    color: Mapped[str | None] = mapped_column(String(20))

    user = relationship("User", back_populates="marginalia_notes")
