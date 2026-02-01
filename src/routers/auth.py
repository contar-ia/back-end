import services
from models import LoginRequest, RegisterRequest
from fastapi import APIRouter, status

auth_router = APIRouter()

@auth_router.post("/login/")
async def execute_login(request: LoginRequest):
    return await services.auth.login_user(request.email, request.password)

@auth_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def execute_user_registration(request: RegisterRequest):
    await services.auth.register_user(request.username, request.email, request.password)
    return { "message": "User created" }

@auth_router.get("/")
async def list_db_users():
    users = await services.auth._list_db_users()
    return users
