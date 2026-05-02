from sqlalchemy import String, Text, Integer, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class PlaylistType(str, enum.Enum):
    problem = "problem"
    question = "question"


class Playlist(Base, TimestampMixin):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    playlist_type: Mapped[PlaylistType] = mapped_column(
        SAEnum(PlaylistType, name="playlisttype"),
        nullable=False,
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    items = relationship(
        "PlaylistItem",
        back_populates="playlist",
        order_by="PlaylistItem.order",
        cascade="all, delete-orphan",
    )


class PlaylistItem(Base):
    __tablename__ = "playlist_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    playlist_id: Mapped[int] = mapped_column(
        ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # One of these is set depending on playlist_type
    problem_id: Mapped[int | None] = mapped_column(
        ForeignKey("problems.id", ondelete="CASCADE"), nullable=True
    )
    question_id: Mapped[int | None] = mapped_column(
        ForeignKey("qna_questions.id", ondelete="CASCADE"), nullable=True
    )
    note: Mapped[str | None] = mapped_column(Text)

    playlist = relationship("Playlist", back_populates="items")
