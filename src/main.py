import logging
import httpx
import routers
from contextlib import asynccontextmanager
from database import db_manager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tentar conectar ao banco, mas não falhar se não conseguir
    await db_manager.connect() # Runs when the server starts
    yield
    # Desconectar apenas se estiver conectado
    if db_manager.connected:
        await db_manager.disconnect() # Runs when the server stops
    
# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI()

app = FastAPI(lifespan=lifespan)

# Register the routes to the fastapi server
app.include_router(routers.llm_router, prefix="/llm") # from docs: "A path prefix must not end with '/', as the routes will start with '/'"
app.include_router(routers.auth_router, prefix="/auth")
app.include_router(routers.stories_router, prefix="/stories")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return { "is_healthy": True }