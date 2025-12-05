"""
Database initialization and setup utilities.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.database.connection import Base, engine
from src.utils.config import settings


async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Import all models to ensure they're registered
        from src.database import models
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


async def drop_tables():
    """Drop all database tables (use with caution)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("⚠️ Database tables dropped!")


async def reset_database():
    """Drop and recreate all tables (development only)."""
    if not settings.debug:
        raise Exception("Database reset only allowed in debug mode!")
    
    await drop_tables()
    await create_tables()
    print("🔄 Database reset complete!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.database.init_db [create|drop|reset]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "create":
        asyncio.run(create_tables())
    elif command == "drop":
        asyncio.run(drop_tables())
    elif command == "reset":
        asyncio.run(reset_database())
    else:
        print("Invalid command. Use 'create', 'drop', or 'reset'")
        sys.exit(1)