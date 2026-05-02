"""Initial schema with full-text search triggers

Revision ID: 0001
Revises:
Create Date: 2026-05-01
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Full-text search triggers — keep search_vector in sync automatically
_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION update_search_vector_writing_posts()
RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.subtitle, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.content, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_writing_posts_search
BEFORE INSERT OR UPDATE ON writing_posts
FOR EACH ROW EXECUTE FUNCTION update_search_vector_writing_posts();

---

CREATE OR REPLACE FUNCTION update_search_vector_courses()
RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.subtitle, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(NEW.description, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_courses_search
BEFORE INSERT OR UPDATE ON courses
FOR EACH ROW EXECUTE FUNCTION update_search_vector_courses();

---

CREATE OR REPLACE FUNCTION update_search_vector_lessons()
RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.content, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_lessons_search
BEFORE INSERT OR UPDATE ON lessons
FOR EACH ROW EXECUTE FUNCTION update_search_vector_lessons();

---

CREATE OR REPLACE FUNCTION update_search_vector_problems()
RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.description, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_problems_search
BEFORE INSERT OR UPDATE ON problems
FOR EACH ROW EXECUTE FUNCTION update_search_vector_problems();

---

CREATE OR REPLACE FUNCTION update_search_vector_concepts()
RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.body, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER trig_concepts_search
BEFORE INSERT OR UPDATE ON concepts
FOR EACH ROW EXECUTE FUNCTION update_search_vector_concepts();
"""

_DROP_TRIGGERS_SQL = """
DROP TRIGGER IF EXISTS trig_writing_posts_search ON writing_posts;
DROP TRIGGER IF EXISTS trig_courses_search ON courses;
DROP TRIGGER IF EXISTS trig_lessons_search ON lessons;
DROP TRIGGER IF EXISTS trig_problems_search ON problems;
DROP TRIGGER IF EXISTS trig_concepts_search ON concepts;
DROP FUNCTION IF EXISTS update_search_vector_writing_posts;
DROP FUNCTION IF EXISTS update_search_vector_courses;
DROP FUNCTION IF EXISTS update_search_vector_lessons;
DROP FUNCTION IF EXISTS update_search_vector_problems;
DROP FUNCTION IF EXISTS update_search_vector_concepts;
"""


def upgrade() -> None:
    # Enums — DO blocks silently skip if type already exists
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('free', 'pro', 'admin');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE difficultylevel AS ENUM ('beginner', 'intermediate', 'advanced');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE roadmapstatus AS ENUM ('writing', 'planned', 'suggested', 'published');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE problemcategory AS ENUM ('architecture', 'training', 'gpu_systems', 'paper_implementations', 'debugging', 'math', 'rl', 'data');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE submissionstatus AS ENUM ('pending', 'running', 'accepted', 'wrong_answer', 'time_limit_exceeded', 'memory_limit_exceeded', 'runtime_error', 'compilation_error');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE questiontype AS ENUM ('conceptual', 'diagnostic');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE playlisttype AS ENUM ('problem', 'question');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE contenttype AS ENUM ('writing_post', 'lesson', 'course', 'problem', 'qna_lab', 'concept');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("username", sa.String(60), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(120)),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("bio", sa.String(500)),
        sa.Column("role", sa.Enum("free", "pro", "admin", name="userrole", create_type=False), nullable=False, server_default="free"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Writing posts
    op.create_table(
        "writing_posts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("subtitle", sa.String(500)),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("marimo_cells", JSONB),
        sa.Column("tags", JSONB),
        sa.Column("cover_image_url", sa.String(500)),
        sa.Column("reading_time_minutes", sa.Integer),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("search_vector", TSVECTOR),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_writing_posts_search", "writing_posts", ["search_vector"], postgresql_using="gin")

    # Problems (before courses — courses FK into problems)
    op.create_table(
        "problems",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("difficulty", sa.Enum("beginner", "intermediate", "advanced", name="difficultylevel", create_type=False), nullable=False),
        sa.Column("category", sa.Enum("architecture", "training", "gpu_systems", "paper_implementations", "debugging", "math", "rl", "data", name="problemcategory", create_type=False), nullable=False),
        sa.Column("starter_code", sa.Text, nullable=False),
        sa.Column("solution_code", sa.Text, nullable=False),
        sa.Column("solution_explanation", sa.Text),
        sa.Column("test_cases", JSONB, nullable=False),
        sa.Column("hints", JSONB),
        sa.Column("tags", JSONB),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("related_post_id", sa.Integer, sa.ForeignKey("writing_posts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("search_vector", TSVECTOR),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_problems_search", "problems", ["search_vector"], postgresql_using="gin")

    # Courses
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("subtitle", sa.String(500)),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("difficulty", sa.Enum("beginner", "intermediate", "advanced", name="difficultylevel", create_type=False), nullable=False),
        sa.Column("cover_image_url", sa.String(500)),
        sa.Column("tags", JSONB),
        sa.Column("prerequisites", JSONB),
        sa.Column("estimated_hours", sa.Integer),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("final_project_problem_id", sa.Integer, sa.ForeignKey("problems.id", ondelete="SET NULL"), nullable=True),
        sa.Column("search_vector", TSVECTOR),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_courses_search", "courses", ["search_vector"], postgresql_using="gin")

    # Chapters
    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("course_id", sa.Integer, sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Lessons
    op.create_table(
        "lessons",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("chapter_id", sa.Integer, sa.ForeignKey("chapters.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("marimo_cells", JSONB),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("reading_time_minutes", sa.Integer),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("problem_id", sa.Integer, sa.ForeignKey("problems.id", ondelete="SET NULL"), nullable=True),
        sa.Column("search_vector", TSVECTOR),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_lessons_search", "lessons", ["search_vector"], postgresql_using="gin")

    # Concepts
    op.create_table(
        "concepts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("example_code", sa.Text),
        sa.Column("related_post_ids", JSONB),
        sa.Column("related_problem_ids", JSONB),
        sa.Column("related_course_ids", JSONB),
        sa.Column("tags", JSONB),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("search_vector", TSVECTOR),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_concepts_search", "concepts", ["search_vector"], postgresql_using="gin")

    # Roadmap
    op.create_table(
        "roadmap_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.Enum("writing", "planned", "suggested", "published", name="roadmapstatus", create_type=False), nullable=False, server_default="planned"),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("upvotes", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # QnA Labs
    op.create_table(
        "qna_labs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("writing_post_id", sa.Integer, sa.ForeignKey("writing_posts.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("lesson_id", sa.Integer, sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True, index=True),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # QnA Questions
    op.create_table(
        "qna_questions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("lab_id", sa.Integer, sa.ForeignKey("qna_labs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("question_type", sa.Enum("conceptual", "diagnostic", name="questiontype", create_type=False), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("expected_answer", sa.Text),
        sa.Column("options", JSONB),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # QnA Responses
    op.create_table(
        "qna_responses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("question_id", sa.Integer, sa.ForeignKey("qna_questions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("response_text", sa.Text, nullable=False),
        sa.Column("selected_option", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Playlists
    op.create_table(
        "playlists",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("slug", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("playlist_type", sa.Enum("problem", "question", name="playlisttype", create_type=False), nullable=False),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Playlist items
    op.create_table(
        "playlist_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("playlist_id", sa.Integer, sa.ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("order", sa.Integer, nullable=False, server_default="0"),
        sa.Column("problem_id", sa.Integer, sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=True),
        sa.Column("question_id", sa.Integer, sa.ForeignKey("qna_questions.id", ondelete="CASCADE"), nullable=True),
        sa.Column("note", sa.Text),
    )

    # Problem submissions
    op.create_table(
        "problem_submissions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("problem_id", sa.Integer, sa.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("code", sa.Text, nullable=False),
        sa.Column("language", sa.String(30), nullable=False, server_default="python"),
        sa.Column("status", sa.Enum("pending", "running", "accepted", "wrong_answer", "time_limit_exceeded", "memory_limit_exceeded", "runtime_error", "compilation_error", name="submissionstatus", create_type=False), nullable=False, server_default="pending"),
        sa.Column("test_results", JSONB),
        sa.Column("execution_time_ms", sa.Integer),
        sa.Column("memory_used_kb", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # User progress
    op.create_table(
        "user_progress",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("content_type", sa.Enum("writing_post", "lesson", "course", "problem", "qna_lab", "concept", name="contenttype", create_type=False), nullable=False),
        sa.Column("content_id", sa.Integer, nullable=False, index=True),
        sa.Column("is_completed", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("progress_pct", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Install full-text search triggers
    for stmt in _TRIGGER_SQL.split("---"):
        stmt = stmt.strip()
        if stmt:
            op.execute(stmt)


def downgrade() -> None:
    op.execute(_DROP_TRIGGERS_SQL)
    op.drop_table("user_progress")
    op.drop_table("problem_submissions")
    op.drop_table("playlist_items")
    op.drop_table("playlists")
    op.drop_table("qna_responses")
    op.drop_table("qna_questions")
    op.drop_table("qna_labs")
    op.drop_table("roadmap_items")
    op.drop_table("concepts")
    op.drop_table("lessons")
    op.drop_table("chapters")
    op.drop_table("courses")
    op.drop_table("problems")
    op.drop_table("writing_posts")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS contenttype")
    op.execute("DROP TYPE IF EXISTS playlisttype")
    op.execute("DROP TYPE IF EXISTS questiontype")
    op.execute("DROP TYPE IF EXISTS submissionstatus")
    op.execute("DROP TYPE IF EXISTS problemcategory")
    op.execute("DROP TYPE IF EXISTS roadmapstatus")
    op.execute("DROP TYPE IF EXISTS difficultylevel")
    op.execute("DROP TYPE IF EXISTS userrole")
