from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    SUBAGENT = "subagent"

class ToolCall(BaseModel):
    id: str
    tool_name: str
    arguments: Dict[str, Any]

class Message(BaseModel):
    role: MessageRole
    content: str
    images: Optional[List[str]] = None  # Base64 string atau path gambar untuk Multimodal Gemma 4 12B
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_llm_dict(self, backend: str = "ollama") -> Dict[str, Any]:
        """Format pesan ke struktur API (mendukung input gambar/multimodal Ollama & OpenAI vision)."""
        payload = {"role": self.role.value, "content": self.content}
        
        # Dukungan multimodal vision Gemma 4 12B
        if self.images and len(self.images) > 0:
            if backend.lower() == "ollama":
                # Ollama menerima field 'images' berisi array string base64
                payload["images"] = self.images
            else:
                # OpenAI vision compatible format
                content_list = [{"type": "text", "text": self.content}]
                for img in self.images:
                    content_list.append({
                        "type": "image_url",
                        "image_url": {"url": img if img.startswith("http") or img.startswith("data:") else f"data:image/jpeg;base64,{img}"}
                    })
                payload["content"] = content_list

        if self.tool_calls:
            payload["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.tool_name, "arguments": str(tc.arguments)}
                }
                for tc in self.tool_calls
            ]
        if self.tool_call_id:
            payload["tool_call_id"] = self.tool_call_id
        if self.name:
            payload["name"] = self.name
        return payload
