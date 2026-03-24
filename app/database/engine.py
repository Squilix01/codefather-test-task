from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from app.core.config import Config

config = Config()


engine = create_async_engine(
    config.db.get_database_url("asyncpg"),
    future=True,
    echo=True,
)