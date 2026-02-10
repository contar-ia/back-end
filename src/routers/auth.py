import services
from models import LoginRequest, RegisterRequest
from fastapi import APIRouter, Header, HTTPException, status

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

@auth_router.get("/me")
async def get_me(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    token = authorization.removeprefix("Bearer ").strip()
    user = await services.auth.get_user_by_session_token(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return user
