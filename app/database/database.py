"""
Módulo de gerenciamento de banco de dados PostgreSQL utilizando asyncpg.

Este módulo define a classe Database, responsável por:
- Estabelecer e encerrar conexões com o banco de dados
- Gerenciar um pool de conexões assíncronas
- Executar consultas SQL (com ou sem retorno de dados)
- Garantir compatibilidade com versões antigas do schema (migrações leves)
- Fornecer uma instância global reutilizável (db_manager)

A conexão utiliza a string definida em app.core.constants.DATABASE_CONNECTION_STRING.

Caso a conexão falhe, a aplicação continua funcionando, porém sem recursos
dependentes de banco de dados.
"""
import asyncpg
import logging
import app.core.constants as const

# Logger específico do módulo
logger = logging.getLogger(__name__)

class Database:
    """
    Classe responsável por gerenciar conexões com o PostgreSQL via asyncpg.

    A classe encapsula um pool de conexões e fornece métodos utilitários
    para execução de queries, buscando simplificar o acesso ao banco
    em toda a aplicação.

    Atributos:
        pool (asyncpg.Pool | None):
            Pool de conexões ativo com o banco de dados.
            Permite reutilização eficiente de conexões.

        connected (bool):
            Indica se a aplicação conseguiu se conectar ao banco.
            Utilizado para evitar operações quando não há conexão.
    """

    def __init__(self):
        """
        Inicializa o gerenciador de banco sem conexão ativa.

        A conexão real é estabelecida posteriormente via método connect().
        """
        self.pool = None
        self.connected = False

    async def connect(self):
        """
        Estabelece conexão com o banco de dados criando um pool asyncpg.

        Também executa pequenas migrações de compatibilidade para garantir
        que colunas adicionais existam na tabela 'users', mesmo em bancos
        mais antigos.

        Operações realizadas:
        - Criação do pool de conexões
        - Atualização do estado interno (connected)
        - Garantia da existência das colunas:
            • institution (TEXT)
            • bio (TEXT)

        Em caso de falha:
        - A aplicação continua rodando
        - Recursos dependentes de banco ficam indisponíveis
        - Logs de aviso são emitidos

        Raises:
            Nenhuma exceção é propagada (tratamento interno).
        """
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(const.DATABASE_CONNECTION_STRING)
                self.connected = True

                # Garante compatibilidade com schemas antigos.
                await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS institution TEXT")
                await self.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT")

                logger.info("Connected to PostgreSQL")

            except Exception as e:
                logger.warning(f"Could not connect to database: {str(e)}")
                logger.warning("Server will run without database features.")
                self.connected = False
                self.pool = None

    async def disconnect(self):
        """
        Encerra o pool de conexões com o banco de dados.

        Deve ser chamado durante o shutdown da aplicação para liberar
        recursos corretamente.
        """
        if self.pool:
            await self.pool.close()

    async def execute(self, query: str, *args):
        """
        Executa uma query SQL que não retorna dados (INSERT, UPDATE, DDL, etc.).

        Args:
            query (str):
                Comando SQL a ser executado.

            *args:
                Parâmetros posicionais para a query.

        Returns:
            str:
                Status da execução retornado pelo PostgreSQL.
                Exemplos:
                - "INSERT 0 1"
                - "UPDATE 1"
                - "CREATE TABLE"

        Raises:
            Exception:
                Se o banco não estiver conectado.
        """
        if not self.connected or not self.pool:
            raise Exception("Database is not connected")

        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)

    async def fetch(self, query: str, *args):
        """
        Executa uma query SQL que retorna múltiplas linhas.

        Args:
            query (str):
                Comando SQL SELECT.

            *args:
                Parâmetros posicionais da query.

        Returns:
            List[asyncpg.Record]:
                Lista de registros retornados.

        Raises:
            Exception:
                Se o banco não estiver conectado.
        """
        if not self.connected or not self.pool:
            raise Exception("Database is not connected")

        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """
        Executa uma query SQL que retorna apenas a primeira linha encontrada.

        Args:
            query (str):
                Comando SQL SELECT.

            *args:
                Parâmetros posicionais da query.

        Returns:
            asyncpg.Record | None:
                Registro encontrado ou None se não houver resultado.

        Raises:
            Exception:
                Se o banco não estiver conectado.
        """
        if not self.connected or not self.pool:
            raise Exception("Database is not connected")

        async with self.pool.acquire() as connection:
            return await connection.fetchrow(query, *args)

# Instância global do gerenciador de banco de dados.
# Deve ser reutilizada por toda a aplicação para evitar múltiplos pools.
db_manager = Database()
