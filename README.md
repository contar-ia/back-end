# Routes:

**POST /llm/generate/**
```
// body
{
    "prompt": "Qual a capital do brasil?"
}
```

rode o comando no terminal:

```bash
curl -X POST "http://localhost:8000/llm/generate/"      -H "Content-Type: application/json"      -d '{"prompt": "Qual a capital do Brasil?"}'
```

# to build: 

```bash
docker compose up --build
```

# to run:

```bash
docker compose up
```

# Containers:

- ollama
- fastapi-app

# Auth (/auth/):

### Registration (/auth/register)
**POST** http://localhost:8000/auth/register
REQUEST
```json
{
	"username": "yoyo",
	"password": "123",
	"email": "yo@yo.com"
}
```
RESPONSE:
```json
{
	"message": "User created"
}
```

### Login (/auth/login)
**POST** http://localhost:8000/auth/login
REQUEST:
```json
{
	"username": "yoyo",
	"password": "123"
}
```
RESPONSE:
```json
{
	"user_id": "f88d1391-da05-4b98-b971-5351d61f047d",
	"status": "authenticated",
	"token": "mocked_token"
}
```

### Rota admin auxiliar para listagem de usuários registrados:
**GET** http://localhost:8000/auth
RESPONSE:
```json
[
	{
		"id": "f88d1391-da05-4b98-b971-5351d61f047d",
		"username": "yoyo",
		"email": "yo@yo.com",
		"pw_hash": "$2b$12$P4sX.Uuf6o06z/.mdC4Bs.hghBqYIxSqOU0MQYuefPoTf0kyz6Jpu"
	}
]
```