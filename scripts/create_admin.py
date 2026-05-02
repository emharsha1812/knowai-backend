"""
Creates (or promotes) the KnowAI admin user.

Usage:
    python scripts/create_admin.py
    python scripts/create_admin.py --password "yourpassword"

Run from the knowai-backend directory with the virtual-env active and
a valid .env (or DATABASE_URL env var) pointing at your Postgres instance.
"""
import asyncio
import argparse
import sys
from pathlib import Path

# Allow imports from the app package when run from the repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole

ADMIN_EMAIL = "harshwardhanfartale.nith@gmail.com"
ADMIN_USERNAME = "harshwardhan"
ADMIN_DISPLAY_NAME = "Harshwardhan Fartale"


async def run(password: str) -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        user = result.scalar_one_or_none()

        if user:
            user.role = UserRole.admin
            user.hashed_password = hash_password(password)
            user.is_active = True
            await session.commit()
            print(f"✓ Existing user promoted to admin: {ADMIN_EMAIL}")
        else:
            user = User(
                email=ADMIN_EMAIL,
                username=ADMIN_USERNAME,
                display_name=ADMIN_DISPLAY_NAME,
                hashed_password=hash_password(password),
                role=UserRole.admin,
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            await session.commit()
            print(f"✓ Admin account created: {ADMIN_EMAIL}")

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote KnowAI admin user")
    parser.add_argument("--password", help="Admin password (prompted if omitted)")
    args = parser.parse_args()

    if args.password:
        password = args.password
    else:
        import getpass
        password = getpass.getpass("Enter admin password: ")
        confirm = getpass.getpass("Confirm password: ")
        if password != confirm:
            print("Passwords do not match.")
            sys.exit(1)

    if len(password) < 8:
        print("Password must be at least 8 characters.")
        sys.exit(1)

    asyncio.run(run(password))


if __name__ == "__main__":
    main()
