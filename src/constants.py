import os

# Declared in docker-compose.yml
OLLAMA_URL=os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL=os.getenv("OLLAMA_MODEL", "llama3.2:latest")

DATABASE_CONNECTION_STRING = "postgresql://contaria:contaria@contaria_db:5432/contaria"