import os
import httpx

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

import json

async def query_ollama(prompt: str, model: str = "llama2") -> str:
    """
    Send a prompt to the local Ollama server and return the response.
    Handles streaming responses from Ollama correctly.
    """
    url = f"{OLLAMA_BASE_URL}/api/generate"
    payload = {"model": model, "prompt": prompt, "stream": True}
    response_text = ""
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", url, json=payload) as response:
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line)
                        response_text += data.get("response", "")
                    except json.JSONDecodeError:
                        pass
    return response_text
