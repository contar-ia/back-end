import httpx
import constants as const

async def send_prompt(prompt: str):
    async with httpx.AsyncClient() as client: 
        response = await client.post(
            const.OLLAMA_URL,
            json={
                "model": const.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=180
        )
        
        response.raise_for_status()
        response_string = response.json().get("response", "")
        return response_string