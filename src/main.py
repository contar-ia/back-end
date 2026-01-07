import httpx
import routers
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(routers.llm_router, prefix="/llm") # from docs: "A path prefix must not end with '/', as the routes will start with '/'"
app.include_router(routers.auth_router, prefix="/auth")

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