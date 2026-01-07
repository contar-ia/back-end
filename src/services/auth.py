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

async def login_user():
    pass

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