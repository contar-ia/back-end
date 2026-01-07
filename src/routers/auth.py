import services
from models import LoginRequest, RegisterRequest
from fastapi import APIRouter

auth_router = APIRouter()

@auth_router.post("/login/")
async def execute_login(request: LoginRequest):
    return {
        "not": "yet implemented" 
    }

@auth_router.post("/register/")
async def execute_user_registration(request: RegisterRequest):
    return {
        "not": "yet implemented"
    }