import asyncpg
import os
import constants as const

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        if not self.pool:
            self.pool = await asyncpg.create_pool(const.DATABASE_CONNECTION_STRING)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        # Returns the status of the query, something like "INSERT 0 1", "UPDATE 1", "CREATE TABLE"
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        # Returns multiple rows as a Record object list.
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        # Returns a single row or none. If multiple rows are match, discard all except the first one
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

db_manager = Database()