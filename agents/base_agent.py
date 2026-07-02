import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from core.message import Message, MessageRole
from core.state import ExecutionState
from core.os_utils import get_os_context_prompt
from models.llm_client import LLMClient
from tools.base_tool import BaseTool

class BaseAgent(ABC):
    """Kelas dasar untuk setiap agen spesialis dalam ekosistem Nvoin AI (Dilengkapi konteks OS Windows & Arch Linux)."""
    def __init__(self, name: str, system_prompt: str, llm_client: LLMClient, tools: List[BaseTool] = None):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in (tools or [])}

    def execute(self, task_prompt: str, state: ExecutionState) -> Tuple[str, bool]:
        """
        Menjalankan tugas agen dengan eksekusi tool berantai (berurutan)
        dan menyisipkan informasi OS (Windows vs Linux Arch) ke dalam prompt.
        """
        os_context = get_os_context_prompt()
        full_system_prompt = f"{self.system_prompt}\n{os_context}"

        messages = [
            Message(role=MessageRole.SYSTEM, content=full_system_prompt),
            Message(role=MessageRole.USER, content=f"Tugas dari Manajer: {task_prompt}")
        ]

        tool_schemas = [t.to_function_definition() for t in self.tools.values()] if self.tools else None

        max_steps = 8
        for step in range(max_steps):
            raw_output = self.llm.generate(messages=messages, tools=tool_schemas)
            
            tool_call = self._parse_tool_request(raw_output)
            if tool_call and tool_call["name"] in self.tools:
                tool_name = tool_call["name"]
                args = tool_call.get("args", {})
                
                tool_output = self.tools[tool_name].execute(**args)
                messages.append(Message(role=MessageRole.ASSISTANT, content=f"Mengeksekusi tool {tool_name} dengan parameter {args}..."))
                messages.append(Message(role=MessageRole.TOOL, content=tool_output, name=tool_name))
            else:
                return raw_output, True

        return "Selesai dengan batas maksimal langkah tool.", True

    def _parse_tool_request(self, response_text: str) -> Dict[str, Any]:
        """Mengekstrak permintaan eksekusi tool jika model mengeluarkan blok JSON khusus tool."""
        try:
            if "tool_call:" in response_text or "function:" in response_text or "{" in response_text:
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx != -1 and end_idx != -1:
                    data = json.loads(response_text[start_idx:end_idx])
                    if "name" in data:
                        return data
        except Exception:
            pass
        return None
