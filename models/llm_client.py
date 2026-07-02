import json
import re
import os
import httpx
from typing import List, Dict, Any, Optional
from core.config import LLMConfig
from core.message import Message

class LLMClient:
    """Klien universal untuk menghubungkan Nvoin AI ke backend Cloud API (Gemini, HuggingFace, Qwen, dan OpenAI-compatible)."""
    def __init__(self, config: LLMConfig):
        self.config = config

    def generate(self, messages: List[Message], temperature: Optional[float] = None, tools: Optional[List[Dict[str, Any]]] = None) -> str:
        temp = temperature if temperature is not None else self.config.temperature
        payload_messages = [m.to_llm_dict(backend=self.config.backend) for m in messages]

        backend_lower = self.config.backend.lower()
        if backend_lower == "gemini":
            res = self._call_gemini(payload_messages, temp, tools)
        elif backend_lower == "huggingface":
            res = self._call_huggingface(payload_messages, temp, tools)
        elif backend_lower == "qwen":
            res = self._call_qwen(payload_messages, temp, tools)
        else:
            res = self._call_openai_compatible(payload_messages, temp, tools)
        return self.clean_deep_think_tags(res)

    def clean_deep_think_tags(self, content: str) -> str:
        """Membersihkan log deep thinking (<think>...</think>) berlebih agar respons cepat & ringkas."""
        if not content:
            return ""
        if "{" in content and "action" in content:
            return content
        return re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

    def _call_gemini(self, messages: List[Dict[str, Any]], temperature: float, tools: Optional[List[Dict[str, Any]]]) -> str:
        gemini_key = os.getenv("GEMINI_API_KEY") or self.config.api_key
        model_id = self.config.model_name if self.config.model_name and "gemini" in self.config.model_name.lower() else "gemini-3.5-flash"
        
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {
            "Authorization": f"Bearer {gemini_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": max(0.01, temperature)
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
            return f'{{"action": "direct_answer", "response": "Error komunikasi dengan Gemini API ({model_id}): {str(e)}"}}'

    def _call_huggingface(self, messages: List[Dict[str, Any]], temperature: float, tools: Optional[List[Dict[str, Any]]]) -> str:
        hf_key = os.getenv("HUGGING_FACE_API_KEY") or self.config.api_key
        model_id = self.config.model_name if self.config.model_name and "gemma" in self.config.model_name.lower() else "google/gemma-4-31B-it"
        
        urls_to_try = [
            "https://router.huggingface.co/v1/chat/completions",
            "https://router.huggingface.co/hf-inference/v1/chat/completions",
            f"https://api-inference.huggingface.co/models/{model_id}/v1/chat/completions"
        ]
        
        headers = {
            "Authorization": f"Bearer {hf_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": max(0.01, temperature),
            "max_tokens": getattr(self.config, "max_tokens", 2048)
        }

        last_err = ""
        for url in urls_to_try:
            try:
                with httpx.Client(timeout=120.0) as client:
                    response = client.post(url, json=payload, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        return data["choices"][0]["message"].get("content", "")
                    else:
                        last_err = f"Status {response.status_code}: {response.text}"
            except Exception as e:
                last_err = str(e)

        return f'{{"action": "direct_answer", "response": "Error komunikasi dengan HuggingFace API ({model_id}): {last_err}"}}'

    def _call_qwen(self, messages: List[Dict[str, Any]], temperature: float, tools: Optional[List[Dict[str, Any]]]) -> str:
        qwen_key = os.getenv("QWEN_MODEL_API") or self.config.api_key
        model_id = self.config.model_name if self.config.model_name and "qwen" in self.config.model_name.lower() else "qwen-plus"
        
        url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {qwen_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": max(0.01, temperature)
        }
        if tools:
            payload["tools"] = tools

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(url, json=payload, headers=headers)
                if response.status_code != 200:
                    url_fallback = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
                    response = client.post(url_fallback, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"].get("content", "")
        except Exception as e:
            return f'{{"action": "direct_answer", "response": "Error komunikasi dengan Qwen DashScope API ({model_id}): {str(e)}"}}'

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
            return f'{{"action": "direct_answer", "response": "Error komunikasi dengan OpenAI-compatible backend: {str(e)}"}}'
