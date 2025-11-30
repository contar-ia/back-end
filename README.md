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