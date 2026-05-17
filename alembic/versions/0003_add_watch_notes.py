"""Add watch_notes table

Revision ID: 0003
Revises: 0002
Create Date: 2026-05-13
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "watch_notes",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("slug", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("youtube_video_id", sa.String(50), nullable=False),
        sa.Column("channel", sa.String(255), nullable=False),
        sa.Column("author", sa.String(255), nullable=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("duration", sa.String(20), nullable=False),
        sa.Column("watched_ratio", sa.Float(), nullable=False, server_default="0"),
        sa.Column("note_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("page_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tag", sa.String(100), nullable=False),
        sa.Column("color", sa.String(50), nullable=False, server_default="lavender"),
        sa.Column("last_note", sa.Text(), nullable=True),
        sa.Column("thumb_bg", sa.String(20), nullable=False, server_default="#1a1a1a"),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("sections", JSONB(), nullable=True),
        sa.Column("pdf_url", sa.String(500), nullable=True),
        sa.Column("view_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("watch_notes")
