"""
One-shot script: delete all courses from the DB except reinforcement-learning-101.
Run from the knowai-backend directory:
    python scripts/clear_courses.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from app.core.config import settings
from app.models.course import Course, Chapter, Lesson

KEEP_SLUG = "reinforcement-learning-101"


async def main():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Course))
            courses = result.scalars().all()

            to_delete = [c for c in courses if c.slug != KEEP_SLUG]
            keep = [c for c in courses if c.slug == KEEP_SLUG]

            if not to_delete:
                print("Nothing to delete — DB already clean.")
            else:
                for course in to_delete:
                    print(f"  Deleting: {course.slug!r} (id={course.id})")
                    await session.delete(course)
                print(f"\nDeleted {len(to_delete)} course(s).")

            if keep:
                print(f"Kept: {keep[0].slug!r}")
            else:
                print("(RL 101 not in DB — it will be served from the catalog fallback)")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
