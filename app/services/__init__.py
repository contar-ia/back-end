"""
Módulo de inicialização do pacote de serviços da aplicação.

Este arquivo controla quais objetos são expostos publicamente quando o
pacote `app.services` é importado.

Ele funciona como uma "interface pública" (API do pacote), permitindo:

• Centralizar imports de serviços
• Simplificar uso em outros módulos
• Evitar imports longos e repetitivos
• Definir explicitamente o que é público no pacote
• Melhorar organização e encapsulamento
"""
from app.services import agents
from app.services import auth
from app.services.agents import send_prompt

# ============================================================================
# EXPORTAÇÃO PÚBLICA DO PACOTE
# ============================================================================
# A variável __all__ define quais símbolos serão exportados.
# Também documenta explicitamente a API pública do pacote.
# ============================================================================
__all__ = [
    "send_prompt",  # Função principal para envio de prompts ao LLM
    "auth",         # Submódulo de autenticação e usuários
    "agents",       # Submódulo com lógica de agentes e integração com LLM
]
