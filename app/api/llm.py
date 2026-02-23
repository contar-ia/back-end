from fastapi import APIRouter
from app.models.models import PromptRequest
from app.services import agents as agents_service

llm_router = APIRouter()

@llm_router.post("/generate/")
async def generate_llm_response(request: PromptRequest):
    llm_response = await agents_service.send_prompt(request.prompt)

    return {
        "answer": llm_response
    }
