from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str
    
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str