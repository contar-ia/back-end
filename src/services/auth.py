from database import db_manager
from fastapi import HTTPException, status
import bcrypt

async def register_user(username: str, email: str, password: str):
    already_registered_username = await db_manager.fetchrow("SELECT * FROM users WHERE username=$1", username)
    if already_registered_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already in use"
        )
    
    already_registered_email = await db_manager.fetchrow("SELECT * FROM users WHERE email=$1", email)
    if already_registered_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    encrypted_password = await _encrypt_password(password)
    query = "INSERT INTO users (username, email, pw_hash) VALUES ($1, $2, $3)"
    await db_manager.execute(query, username, email, encrypted_password)

async def login_user(username: str, password: str):
    query = "SELECT id, pw_hash FROM users WHERE username = $1"
    user_record = await db_manager.fetchrow(query, username)

    if not user_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    is_valid = await _verify_password(password, user_record["pw_hash"])
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return {
        "user_id": user_record["id"],
        "status": "authenticated",
        "token": "mocked_token"
    }

async def _encrypt_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

async def _verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

async def _list_db_users():
    found_users = await db_manager.fetch("SELECT * FROM users")
    return found_users