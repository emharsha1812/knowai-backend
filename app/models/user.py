from sqlalchemy import String, Boolean, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.core.database import Base
from app.models.base import TimestampMixin
import enum


class UserRole(str, enum.Enum):
    free = "free"
    pro = "pro"
    admin = "admin"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    bio: Mapped[str | None] = mapped_column(String(500))
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="userrole"),
        default=UserRole.free,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    submissions = relationship("ProblemSubmission", back_populates="user", lazy="dynamic")
    qna_responses = relationship("QnaResponse", back_populates="user", lazy="dynamic")
    progress_records = relationship("UserProgress", back_populates="user", lazy="dynamic")
