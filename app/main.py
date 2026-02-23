import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import db_manager
from app.api.llm import llm_router
from app.api.auth import auth_router
from app.api.stories import stories_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Conectar ao banco ao iniciar
    await db_manager.connect()
    yield
    # Desconectar ao encerrar
    if db_manager.connected:
        await db_manager.disconnect()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI(lifespan=lifespan)

# Registrar rotas
app.include_router(llm_router, prefix="/llm")
app.include_router(auth_router, prefix="/auth")
app.include_router(stories_router, prefix="/stories")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return {"is_healthy": True}
