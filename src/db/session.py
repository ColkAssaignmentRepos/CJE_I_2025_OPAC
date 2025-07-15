from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import Config

app_config = Config()

# Create an async engine instance
async_engine = create_async_engine(app_config.ASYNC_DATABASE_URL)

# Create a session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[sessionmaker, None]:
    """
    Dependency provider for database sessions.
    Yields a session and ensures it's closed after use.
    """
    async with AsyncSessionLocal() as session:
        yield session
