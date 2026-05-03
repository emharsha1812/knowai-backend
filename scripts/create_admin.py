"""
Creates (or promotes) the KnowAI admin user.

Usage:
    python scripts/create_admin.py --email you@example.com --username you --name "Your Name"
    python scripts/create_admin.py --email you@example.com --password "yourpassword"

Run from the knowai-backend directory with the virtual-env active and
a valid .env (or DATABASE_URL env var) pointing at your Postgres instance.
"""
import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.models.user import User, UserRole


async def run(email: str, username: str, display_name: str, password: str) -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async with Session() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if user:
            user.role = UserRole.admin
            user.hashed_password = hash_password(password)
            user.is_active = True
            await session.commit()
            print(f"✓ Existing user promoted to admin: {email}")
        else:
            user = User(
                email=email,
                username=username,
                display_name=display_name,
                hashed_password=hash_password(password),
                role=UserRole.admin,
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            await session.commit()
            print(f"✓ Admin account created: {email}")

    await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or promote KnowAI admin user")
    parser.add_argument("--email", required=True, help="Admin email address")
    parser.add_argument("--username", required=True, help="Admin username")
    parser.add_argument("--name", required=True, dest="display_name", help="Admin display name")
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

    asyncio.run(run(args.email, args.username, args.display_name, password))


if __name__ == "__main__":
    main()
