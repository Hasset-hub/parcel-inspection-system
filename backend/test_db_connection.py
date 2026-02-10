import asyncio
from sqlalchemy import select, text
from app.db.session import async_session, engine
from app.models.user import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_connection():
    """Test database connection"""
    
    logger.info("Testing database connection...")
    
    async with engine.begin() as conn:
        # Test raw SQL
        result = await conn.execute(text("SELECT version();"))
        version = result.scalar()
        logger.info(f" PostgreSQL version: {version}")
    
    logger.info("Testing async session...")
    
    async with async_session() as session:
        # Test query
        result = await session.execute(select(User))
        users = result.scalars().all()
        logger.info(f" Found {len(users)} users in database")
        
        for user in users:
            logger.info(f"   - {user.username} ({user.role})")
    
    logger.info(" All database tests passed!")

if __name__ == "__main__":
    asyncio.run(test_connection())
