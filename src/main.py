import logging
import httpx
import services
import routers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = FastAPI()

app.include_router(routers.llm_router, prefix="/llm") # from docs: "A path prefix must not end with '/', as the routes will start with '/'"
app.include_router(routers.stories_router, prefix="/stories")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health():
    return { "is_healthy": True }