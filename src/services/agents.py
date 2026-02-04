import httpx
import constants as const

async def send_prompt(prompt: str, timeout: int = 60):
    """
    Envia prompt para Ollama com timeout configurável.
    
    Args:
        prompt: O prompt a ser enviado
        timeout: Timeout em segundos (padrão 60 para validações rápidas, 120 para gerações)
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
        
        response.raise_for_status()
        response_string = response.json().get("response", "")
        return response_string