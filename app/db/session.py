
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine , async_sessionmaker , AsyncSession
from dotenv import load_dotenv
import os


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("database path is wrong")



engine= create_async_engine(
    DATABASE_URL,
    echo=False,              # True only in development
    pool_size=10,     # min connection 
    max_overflow=20, # max Connection 
    pool_timeout=30,
    pool_pre_ping=True,
)


AsyncLocalSession = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncLocalSession() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise