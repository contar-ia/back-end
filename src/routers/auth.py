import services
from models import LoginRequest, RegisterRequest
from fastapi import APIRouter

auth_router = APIRouter()

@auth_router.post("/login/")
async def execute_login(request: LoginRequest):
    await services.auth.login_user()
    return {
        "not": "yet implemented" 
    }

@auth_router.post("/register/")
async def execute_user_registration(request: RegisterRequest):
    await services.auth.register_user(request.username, request.email, request.password)
    return {
        "not": "yet implemented"
    }

@auth_router.get("/")
async def list_db_users():
    users = await services.auth._list_db_users()
    return users
