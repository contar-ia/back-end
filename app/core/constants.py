"""
Módulo de configurações da aplicação.

Este arquivo centraliza variáveis de configuração obtidas a partir de
variáveis de ambiente (environment variables), permitindo que o sistema
seja configurado de forma flexível para diferentes ambientes, como:

- Desenvolvimento local
- Testes
- Produção
- Containers (Docker/Kubernetes)
- Serviços em nuvem

Caso as variáveis de ambiente não estejam definidas, valores padrão
(default) são utilizados.
"""
import os

# URL da API do Ollama responsável pela geração de texto via LLM
# Pode ser configurada pela variável de ambiente OLLAMA_API_URL
#
# Valor padrão:
#   http://localhost:11434/api/generate
#
# Usada para comunicação com o serviço Ollama executando localmente
# ou remotamente.
OLLAMA_URL = os.getenv(
    "OLLAMA_API_URL",
    "http://localhost:11434/api/generate"
)

# Nome ou identificador do modelo LLM utilizado pelo Ollama
# Pode ser configurado pela variável de ambiente OLLAMA_MODEL
#
# Valor padrão:
#   llama3.2:latest
#
# Define qual modelo será usado para gerar respostas (ex.: Llama, Mistral, etc.).
OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2:latest"
)

# String de conexão com o banco de dados PostgreSQL
# Pode ser configurada pela variável de ambiente DATABASE_URL
#
# Formato esperado:
#   postgresql://usuario:senha@host:porta/banco
#
# Valor padrão:
#   postgresql://contaria:contaria@localhost:5432/contaria
#
# Utilizada pelo gerenciador de banco de dados da aplicação para
# estabelecer conexões e executar consultas.
DATABASE_CONNECTION_STRING = os.getenv(
    "DATABASE_URL",
    "postgresql://contaria:contaria@localhost:5432/contaria"
)
