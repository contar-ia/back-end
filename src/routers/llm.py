import services
from models import PromptRequest
from fastapi import APIRouter

llm_router = APIRouter()

@llm_router.post("/generate/")
async def generate_llm_response(request: PromptRequest):
    llm_response = await services.send_prompt(request.prompt)
    return {
        "answer": llm_response
    }