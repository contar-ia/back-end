import asyncpg
import os
import logging
import constants as const

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
                logger.info("✅ Conectado ao banco de dados PostgreSQL")
            except Exception as e:
                logger.warning(f"⚠️  Não foi possível conectar ao banco de dados: {str(e)}")
                logger.warning("⚠️  Servidor continuará sem banco de dados. Funcionalidades que dependem do banco não estarão disponíveis.")
                self.connected = False
                self.pool = None

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        # Returns the status of the query, something like "INSERT 0 1", "UPDATE 1", "CREATE TABLE"
        if not self.connected or not self.pool:
            raise Exception("Banco de dados não está conectado")
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        # Returns multiple rows as a Record object list.
        if not self.connected or not self.pool:
            raise Exception("Banco de dados não está conectado")
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        # Returns a single row or none. If multiple rows are match, discard all except the first one
        if not self.connected or not self.pool:
            raise Exception("Banco de dados não está conectado")
        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

db_manager = Database()