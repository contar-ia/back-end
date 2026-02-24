"""
Módulo de serviços de autenticação e gerenciamento de usuários.

Este módulo implementa a camada de serviço responsável por operações
relacionadas a usuários dentro da aplicação FastAPI, incluindo:

Funcionalidades principais:
- Registro de novos usuários
- Autenticação por email ou username
- Criptografia e verificação de senhas com bcrypt
- Criação e validação de sessões persistentes
- Recuperação de usuário autenticado via token
- Atualização de perfil do usuário

Características de segurança:
- Senhas nunca são armazenadas em texto puro
- Uso de hashing forte com salt (bcrypt)
- Verificação de conflitos de username e email
- Tokens de sessão com expiração automática
- Proteção contra ambiguidade de identificadores no login

Dependências:
- db_manager: Gerenciador de acesso assíncrono ao banco de dados
- FastAPI HTTPException: Tratamento padronizado de erros HTTP
- bcrypt: Hash seguro de senhas
- datetime: Controle de expiração de sessões
"""
from app.database.database import db_manager
from fastapi import HTTPException, status
from app.models.models import UpdateProfileRequest
import bcrypt
from datetime import datetime, timedelta, timezone

async def register_user(username: str, email: str, password: str):
    """
    Registra um novo usuário no sistema.

    Este método:
    1. Normaliza username e email (remove espaços e coloca email em lowercase).
    2. Verifica se já existe usuário com mesmo username ou email.
    3. Criptografa a senha usando bcrypt.
    4. Insere o novo usuário na tabela `users`.

    Args:
        username (str): Nome de usuário escolhido.
        email (str): Email do usuário.
        password (str): Senha em texto puro.

    Raises:
        HTTPException (409 CONFLICT):
            - Se o username já estiver em uso.
            - Se o email já estiver registrado.

    Returns:
        None
    """
    username = username.strip()
    email = email.strip().lower()

    already_registered_username = await db_manager.fetchrow(
        "SELECT * FROM users WHERE username = $1 OR LOWER(email) = LOWER($1)",
        username,
    )
    if already_registered_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already in use"
        )

    already_registered_email = await db_manager.fetchrow(
        "SELECT * FROM users WHERE LOWER(email) = LOWER($1) OR username = $1",
        email,
    )
    if already_registered_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    encrypted_password = await _encrypt_password(password)
    query = "INSERT INTO users (username, email, pw_hash) VALUES ($1, $2, $3)"
    await db_manager.execute(query, username, email, encrypted_password)

async def login_user(email: str, password: str):
    """
    Autentica um usuário usando email ou username.

    Fluxo:
    1. Normaliza o identificador.
    2. Busca por correspondência tanto em email quanto em username.
    3. Evita ambiguidade caso exista:
       - Um usuário com aquele email
       - Outro usuário com aquele mesmo valor como username
    4. Valida a senha com bcrypt.
    5. Cria uma sessão e retorna token de autenticação.

    Args:
        email (str): Pode ser email ou username.
        password (str): Senha em texto puro.

    Raises:
        HTTPException:
            401 UNAUTHORIZED → Credenciais inválidas.
            409 CONFLICT → Identificador ambíguo.

    Returns:
        dict: Dados do usuário autenticado contendo:
            - user_id
            - status
            - username
            - email
            - institution
            - bio
            - token (session_token)
    """
    login_identifier = email.strip()
    normalized_email = login_identifier.lower()

    email_match = await db_manager.fetchrow(
        "SELECT * FROM users WHERE LOWER(email) = LOWER($1) LIMIT 1",
        normalized_email,
    )
    username_match = await db_manager.fetchrow(
        "SELECT * FROM users WHERE username = $1 LIMIT 1",
        login_identifier,
    )

    # Evita autenticar uma conta errada quando o mesmo identificador existe
    # como email de um usuario e username de outro usuario.
    if email_match and username_match and email_match["id"] != username_match["id"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ambiguous login identifier. Use your email address or change your username."
        )

    user_record = email_match or username_match

    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    is_valid = await _verify_password(password, user_record["pw_hash"])
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return {
        "user_id": user_record["id"],
        "status": "authenticated",
        "username": user_record["username"],
        "email": user_record["email"],
        "institution": user_record.get("institution"),
        "bio": user_record.get("bio"),
        "token": await create_session(user_record["id"]),
    }

async def _encrypt_password(password: str) -> str:
    """
    Gera hash seguro da senha utilizando bcrypt.

    Args:
        password (str): Senha em texto puro.

    Returns:
        str: Hash da senha em formato string (UTF-8).
    """
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")

async def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha informada corresponde ao hash armazenado.

    Args:
        plain_password (str): Senha em texto puro.
        hashed_password (str): Hash armazenado no banco.

    Returns:
        bool: True se a senha for válida, False caso contrário.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

async def _list_db_users():
    """
    Lista todos os usuários cadastrados no banco de dados.

    ⚠ Método auxiliar, utilizado para debug ou administração.

    Returns:
        list: Registros completos da tabela `users`.
    """
    found_users = await db_manager.fetch("SELECT * FROM users")
    return found_users

async def create_session(user_id: str):
    """
    Cria uma nova sessão para o usuário.

    A sessão:
    - Possui validade de 7 dias.
    - Gera automaticamente um `session_token`.
    - É armazenada na tabela `sessions`.

    Args:
        user_id (str): ID do usuário autenticado.

    Returns:
        str: Token de sessão gerado.
    """
    expiration = datetime.now(timezone.utc) + timedelta(days=7)

    query = """
        INSERT INTO sessions (user_id, expires_at)
        VALUES ($1, $2)
        RETURNING session_token
    """
    row = await db_manager.fetchrow(query, user_id, expiration)
    return row["session_token"]

async def _get_session_user_row(token: str):
    """
    Recupera os dados do usuário associados a um token de sessão válido.

    Valida:
    - Existência da sessão.
    - Não expiração do token.

    Args:
        token (str): Session token.

    Returns:
        dict | None:
            Dados do usuário + expires_at se válido.
            None se inválido ou expirado.
    """
    if not token:
        return None

    query = """
        SELECT u.id, u.username, u.email, u.institution, u.bio, s.expires_at
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.session_token = $1
        LIMIT 1
    """
    row = await db_manager.fetchrow(query, token)
    if not row:
        return None

    if row["expires_at"] and row["expires_at"] < datetime.now(timezone.utc):
        return None

    return row

async def get_user_by_session_token(token: str):
    """
    Retorna dados públicos do usuário autenticado via token.

    Args:
        token (str): Token de sessão.

    Returns:
        dict | None:
            - user_id
            - username
            - email
            - institution
            - bio
        None se token inválido ou expirado.
    """
    row = await _get_session_user_row(token)
    if not row:
        return None

    return {
        "user_id": row["id"],
        "username": row["username"],
        "email": row["email"],
        "institution": row.get("institution"),
        "bio": row.get("bio"),
    }

async def update_user_by_session_token(token: str, request: UpdateProfileRequest):
    """
    Atualiza os dados do usuário autenticado.

    Regras:
    - Token deve ser válido.
    - Username e email não podem estar vazios.
    - Username e email devem ser únicos no sistema.
    - Não pode haver conflito com outro usuário.

    Args:
        token (str): Token de sessão válido.
        request (UpdateProfileRequest): Objeto contendo:
            - username
            - email
            - institution (opcional)
            - bio (opcional)

    Raises:
        HTTPException:
            401 UNAUTHORIZED → Token inválido.
            400 BAD REQUEST → Campos obrigatórios vazios.
            409 CONFLICT → Username ou email já em uso.

    Returns:
        dict: Dados atualizados do usuário.
    """
    row = await _get_session_user_row(token)
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    username = request.username.strip()
    email = request.email.strip().lower()
    institution = request.institution.strip() if request.institution else None
    bio = request.bio.strip() if request.bio else None

    if not username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username is required")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")

    conflict_username = await db_manager.fetchrow(
        "SELECT id FROM users WHERE (username = $1 OR LOWER(email) = LOWER($1)) AND id <> $2",
        username,
        row["id"],
    )
    if conflict_username:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already in use")

    conflict_email = await db_manager.fetchrow(
        "SELECT id FROM users WHERE (LOWER(email) = LOWER($1) OR username = $1) AND id <> $2",
        email,
        row["id"],
    )
    if conflict_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    updated = await db_manager.fetchrow(
        """
        UPDATE users
        SET username = $1, email = $2, institution = $3, bio = $4
        WHERE id = $5
        RETURNING id, username, email, institution, bio
        """,
        username,
        email,
        institution,
        bio,
        row["id"],
    )

    return {
        "user_id": updated["id"],
        "username": updated["username"],
        "email": updated["email"],
        "institution": updated.get("institution"),
        "bio": updated.get("bio"),
    }
