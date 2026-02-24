"""
Módulo responsável pela comunicação assíncrona com o servidor Ollama.

Este arquivo define a função `send_prompt`, que atua como uma camada
de abstração para envio de prompts ao modelo de linguagem (LLM).

Responsabilidades:

• Encapsular a chamada HTTP ao servidor Ollama
• Aplicar timeout configurável
• Padronizar formato da requisição
• Extrair apenas o conteúdo relevante da resposta
• Propagar erros HTTP quando necessário

Isso permite alterar modelo ou endpoint sem modificar a lógica da aplicação.
"""
import httpx
import app.core.constants as const

async def send_prompt(prompt: str, timeout: int = 60):
    """
    Envia um prompt para o servidor Ollama e retorna a resposta do modelo.

    A comunicação é feita via HTTP POST utilizando httpx.AsyncClient,
    permitindo execução não bloqueante (async/await).

    Args:
        prompt (str):
            Texto que será enviado ao modelo de linguagem.

        timeout (int, opcional):
            Tempo máximo (em segundos) para aguardar a resposta.
            Padrão: 60 segundos.
            Pode ser aumentado para gerações mais longas (ex: 120s).

    Fluxo da requisição:
        1. Cria cliente HTTP assíncrono.
        2. Envia POST para const.OLLAMA_URL.
        3. Define payload com:
            - model  → nome do modelo configurado
            - prompt → texto enviado
            - stream → False (resposta completa, não streaming)
        4. Valida status HTTP.
        5. Extrai campo "response" do JSON retornado.

    Returns:
        str:
            Texto gerado pelo modelo.
            Retorna string vazia caso o campo "response" não exista.

    Raises:
        httpx.HTTPStatusError:
            Se o servidor retornar erro HTTP (4xx ou 5xx).

        httpx.RequestError:
            Se houver erro de conexão, timeout ou falha de rede.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            const.OLLAMA_URL,
            json={
                "model": const.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=timeout
        )

        # Lança exceção automática se o status não for 2xx
        response.raise_for_status()

        # Extrai o campo "response" do JSON retornado
        response_string = response.json().get("response", "")

        return response_string
