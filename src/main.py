from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def health():
    return { "is_healthy": True }