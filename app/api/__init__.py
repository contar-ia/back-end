"""
Módulo agregador de rotas da aplicação FastAPI.

Este arquivo centraliza a importação e exposição pública dos roteadores
(APIRouter) responsáveis por diferentes domínios da API.
"""
from app.api.llm import llm_router
from app.api.auth import auth_router
from app.api.stories import stories_router


# Define a interface pública do módulo
__all__ = [
    "llm_router",      # Router de funcionalidades de LLM
    "auth_router",     # Router de autenticação
    "stories_router",  # Router de gerenciamento de histórias
]
