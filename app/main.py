"""
Arquivo principal da aplicação FastAPI.

Responsabilidades deste módulo:

• Inicializar a aplicação FastAPI
• Configurar ciclo de vida (startup/shutdown)
• Gerenciar conexão com banco de dados
• Registrar rotas da API
• Configurar logging global
• Configurar política de CORS
• Expor endpoint de health check
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import db_manager
from app.api.llm import llm_router
from app.api.auth import auth_router
from app.api.stories import stories_router

# ============================================================================
# LIFESPAN (STARTUP / SHUTDOWN)
# ============================================================================
# Controla o ciclo de vida da aplicação.
# Executa automaticamente ao iniciar e encerrar o servidor.
# ============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia eventos de inicialização e finalização da aplicação.

    Startup:
        - Conecta ao banco de dados via db_manager.

    Shutdown:
        - Fecha pool de conexões se estiver conectado.

    O uso de asynccontextmanager é a forma moderna recomendada
    pelo FastAPI para controle de ciclo de vida.
    """
    await db_manager.connect()

    yield

    if db_manager.connected:
        await db_manager.disconnect()

# ============================================================================
# CONFIGURAÇÃO DE LOGGING
# ============================================================================
# Define formato e nível global de logs da aplicação.
#
# level=logging.INFO:
#   Exibe logs informativos, avisos e erros.
#
# format:
#   Timestamp - nome do logger - nível - mensagem
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ============================================================================
# INSTÂNCIA PRINCIPAL DO FASTAPI
# ============================================================================
# A aplicação é criada com o gerenciador de lifespan configurado.
# ============================================================================
app = FastAPI(lifespan=lifespan)

# ============================================================================
# REGISTRO DE ROTAS
# ============================================================================
# Cada router organiza endpoints por domínio.
#
# Prefixos:
#   /llm      → endpoints relacionados a geração via LLM
#   /auth     → autenticação e usuários
#   /stories  → CRUD e interações com histórias
# ============================================================================
app.include_router(llm_router, prefix="/llm")
app.include_router(auth_router, prefix="/auth")
app.include_router(stories_router, prefix="/stories")

# ============================================================================
# CONFIGURAÇÃO DE CORS
# ============================================================================
# Permite que clientes externos (ex: frontend React, mobile, etc.)
# acessem a API mesmo estando em outro domínio.
#
# allow_origins=["*"]:
#   Permite qualquer origem (adequado para desenvolvimento).
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# ENDPOINT DE HEALTH CHECK
# ============================================================================
# Utilizado para:
#   - Monitoramento
#   - Testes automatizados
#   - Verificação de disponibilidade (ex: Docker, Kubernetes)
# ============================================================================
@app.get("/")
async def health():
    """
    Endpoint simples para verificar se a API está ativa.

    Returns:
        dict:
            {
                "is_healthy": True
            }
    """
    return {"is_healthy": True}
