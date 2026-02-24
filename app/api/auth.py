"""
Módulo de rotas de autenticação e gerenciamento de usuário.

Este módulo define os endpoints relacionados ao ciclo de vida de usuários
na aplicação, incluindo:

- Login de usuário
- Registro de novo usuário
- Listagem de usuários (debug/admin)
- Recuperação do perfil do usuário autenticado
- Atualização do perfil do usuário autenticado
"""
from fastapi import APIRouter, Header, HTTPException, status
from app.services import auth as auth_service
from app.models.models import LoginRequest, RegisterRequest, UpdateProfileRequest

# Instância do roteador responsável pelos endpoints de autenticação
auth_router = APIRouter()

@auth_router.post("/login/")
async def execute_login(request: LoginRequest):
    """
    Realiza o login do usuário.

    Recebe credenciais (email e senha) e delega a autenticação
    ao serviço de autenticação.

    Parâmetros:
        request (LoginRequest): Objeto contendo email e senha.

    Retorno:
        Resultado da autenticação retornado pelo serviço,
        normalmente contendo token de sessão e dados do usuário.
    """
    return await auth_service.login_user(request.email, request.password)

@auth_router.post("/register/", status_code=status.HTTP_201_CREATED)
async def execute_user_registration(request: RegisterRequest):
    """
    Registra um novo usuário no sistema.

    Cria uma nova conta com username, email e senha fornecidos.

    Parâmetros:
        request (RegisterRequest): Dados necessários para criação do usuário.

    Retorno:
        dict: Mensagem de confirmação da criação do usuário.

    Status Code:
        201 Created — Usuário criado com sucesso.
    """
    await auth_service.register_user(request.username, request.email, request.password)
    return {"message": "User created"}

@auth_router.get("/")
async def list_db_users():
    """
    Lista todos os usuários armazenados no banco de dados.

    Observação:
        Este endpoint pode ser destinado a fins administrativos
        ou de depuração, pois expõe todos os usuários.

    Retorno:
        Lista de usuários conforme retornado pelo serviço de autenticação.
    """
    users = await auth_service._list_db_users()
    return users

@auth_router.get("/me")
async def get_me(authorization: str | None = Header(default=None)):
    """
    Obtém os dados do usuário autenticado.

    Requer um token de sessão válido no header Authorization
    no formato Bearer.

    Parâmetros:
        authorization (str | None): Header Authorization contendo o token.

    Retorno:
        Dados do usuário autenticado.

    Exceções:
        HTTPException 401 — Caso o token esteja ausente, mal formatado
        ou inválido.
    """
    # Verifica presença e formato do header Authorization
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # Extrai o token removendo o prefixo "Bearer "
    token = authorization.removeprefix("Bearer ").strip()

    # Recupera usuário associado ao token
    user = await auth_service.get_user_by_session_token(token)

    # Caso não exista usuário válido para o token
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return user

@auth_router.put("/me")
async def update_me(request: UpdateProfileRequest, authorization: str | None = Header(default=None)):
    """
    Atualiza os dados do usuário autenticado.

    Requer autenticação via token de sessão no header Authorization.

    Parâmetros:
        request (UpdateProfileRequest): Dados atualizados do perfil.
        authorization (str | None): Header Authorization contendo o token.

    Retorno:
        Resultado da atualização retornado pelo serviço.

    Exceções:
        HTTPException 401 — Caso o token esteja ausente, inválido
        ou mal formatado.
    """
    # Verifica presença e formato do header Authorization
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    # Extrai o token
    token = authorization.removeprefix("Bearer ").strip()

    # Atualiza usuário associado ao token
    return await auth_service.update_user_by_session_token(token, request)
