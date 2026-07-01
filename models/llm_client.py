import json
import httpx
from typing import List, Dict, Any, Optional
from core.config import LLMConfig
from core.message import Message

class LLMClient:
    """Klien universal untuk menghubungkan Nvoin AI ke backend LLM open source (Ollama/vLLM dengan dukungan Multimodal)."""
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate(self, messages: List[Message], temperature: Optional[float] = None, tools: Optional[List[Dict[str, Any]]] = None) -> str:
        temp = temperature if temperature is not None else self.config.temperature
        payload_messages = [m.to_llm_dict(backend=self.config.backend) for m in messages]

        if self.config.backend.lower() == "ollama":
            return self._call_ollama(payload_messages, temp, tools)
        else:
            return self._call_openai_compatible(payload_messages, temp, tools)

    def _call_ollama(self, messages: List[Dict[str, Any]], temperature: float, tools: Optional[List[Dict[str, Any]]]) -> str:
        url = f"{self.config.base_url.rstrip('/')}/api/chat"
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature}
        }
        if tools:
            payload["tools"] = tools

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("message", {}).get("content", "")
        except Exception as e:
            return f"{{\"action\": \"direct_answer\", \"response\": \"Error komunikasi dengan Ollama backend: {str(e)}\"}}"

    def _call_openai_compatible(self, messages: List[Dict[str, Any]], temperature: float, tools: Optional[List[Dict[str, Any]]]) -> str:
        url = f"{self.config.base_url.rstrip('/')}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": temperature
        }
        if tools:
            payload["tools"] = tools

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"].get("content", "")
        except Exception as e:
            return f"{{\"action\": \"direct_answer\", \"response\": \"Error komunikasi dengan OpenAI-compatible backend: {str(e)}\"}}"
