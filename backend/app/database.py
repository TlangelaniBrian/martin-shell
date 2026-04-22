from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

_is_postgres = settings.database_url.startswith("postgresql")
engine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
    # Pool tuning only applies to PostgreSQL; SQLite uses a StaticPool
    **({
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 300,  # Recycle before Neon's ~13-min idle timeout
    } if _is_postgres else {}),
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_async_session():
    async with async_session_maker() as session:
        yield session
