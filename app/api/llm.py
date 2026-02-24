"""
Módulo de rotas relacionadas a LLM (Large Language Models).

Este módulo define os endpoints responsáveis por interagir com agentes
baseados em modelos de linguagem, permitindo o envio de prompts e a
geração de respostas automáticas.
"""
from fastapi import APIRouter
from app.models.models import PromptRequest
from app.services import agents as agents_service

# Instância do roteador responsável pelos endpoints de LLM
llm_router = APIRouter()

@llm_router.post("/generate/")
async def generate_llm_response(request: PromptRequest):
    """
    Gera uma resposta a partir de um prompt enviado pelo usuário.

    Este endpoint recebe um texto (prompt), encaminha-o ao serviço
    de agentes de LLM e retorna a resposta gerada pelo modelo.

    Parâmetros:
        request (PromptRequest): Objeto contendo o prompt a ser processado.

    Retorno:
        dict: Um dicionário contendo a resposta gerada pelo modelo
        no campo "answer".

        Exemplo:
            {
                "answer": "Resposta gerada pelo modelo"
            }

    Observações:
        - A lógica de geração é tratada pelo serviço agents_service.
        - Este endpoint atua apenas como interface HTTP.
    """
    # Envia o prompt ao serviço responsável pelos agentes de LLM
    llm_response = await agents_service.send_prompt(request.prompt)

    # Retorna a resposta formatada
    return {
        "answer": llm_response
    }
