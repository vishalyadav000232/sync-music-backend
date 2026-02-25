import asyncio
from app.db.session import async_engine  # your Async SQLAlchemy engine
from app.db.base import Base  # declarative base with all models

async def init_db():
    """
    This function creates all tables defined in your SQLAlchemy models.
    """
    async with async_engine.begin() as conn:
        # Drop all tables (optional)
        # await conn.run_sync(Base.metadata.drop_all)

        # Create tables
        await conn.run_sync(Base.metadata.create_all)
        print("✅ All tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())