"""
One-shot script: creates all DB tables and upserts an admin user.

Usage:
    cd backend
    python create_admin.py [email] [password]

Defaults:
    email:    admin@martin.local
    password: Admin1234!
"""
import asyncio
import sys

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings
from app.database import Base
from app.models import ai_settings, refresh_token  # noqa: F401 — register models
from app.models.user import User, UserRole


async def main(email: str, password: str) -> None:
    engine = create_async_engine(settings.database_url)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created (or already exist)")

    async with Session() as session:
        result = await session.execute(select(User).where(User.email == email))
        existing = result.unique().scalar_one_or_none()

        if existing:
            # Promote to admin and verify
            await session.execute(
                update(User)
                .where(User.email == email)
                .values(role=UserRole.admin, is_verified=True, is_active=True)
            )
            await session.commit()
            print(f"✓ Existing user {email!r} promoted to admin")
        else:
            # Create via fastapi-users UserManager so password is hashed correctly
            from fastapi_users.password import PasswordHelper

            helper = PasswordHelper()
            hashed = helper.hash(password)

            import uuid
            user = User(
                id=uuid.uuid4(),
                email=email,
                hashed_password=hashed,
                is_active=True,
                is_verified=True,
                is_superuser=False,
                role=UserRole.admin,
            )
            session.add(user)
            await session.commit()
            print(f"✓ Admin user created: {email!r}")

    print(f"\nLogin at http://localhost:3000/sign-in")
    print(f"  Email:    {email}")
    print(f"  Password: {password}")
    await engine.dispose()


if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "admin@martin.local"
    password = sys.argv[2] if len(sys.argv) > 2 else "Admin1234!"
    asyncio.run(main(email, password))
