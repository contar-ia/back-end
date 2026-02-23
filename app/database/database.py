import asyncpg
import logging
import app.core.constants as const

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None
        self.connected = False

    async def connect(self):
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(const.DATABASE_CONNECTION_STRING)
                self.connected = True

                # Ensure profile columns exist in older databases.
                await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS institution TEXT")
                await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT")

                logger.info("Connected to PostgreSQL")
            except Exception as e:
                logger.warning(f"Could not connect to database: {str(e)}")
                logger.warning("Server will run without database features.")
                self.connected = False
                self.pool = None

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        # Returns status like: INSERT 0 1, UPDATE 1, CREATE TABLE
        if not self.connected or not self.pool:
            raise Exception("Database is not connected")
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        # Returns multiple rows as a list of asyncpg Record.
        if not self.connected or not self.pool:
            raise Exception("Database is not connected")
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        # Returns first matching row or None.
        if not self.connected or not self.pool:
            raise Exception("Database is not connected")
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

db_manager = Database()
