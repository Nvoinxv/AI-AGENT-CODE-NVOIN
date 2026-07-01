import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from core.message import Message, MessageRole
from core.state import ExecutionState
from models.llm_client import LLMClient
from tools.base_tool import BaseTool

class BaseAgent(ABC):
    """Kelas dasar untuk setiap sub-agen dalam arsitektur Fugu."""
    def __init__(self, name: str, system_prompt: str, llm_client: LLMClient, tools: List[BaseTool] = None):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = llm_client
        self.tools = {tool.name: tool for tool in (tools or [])}

    def execute(self, task_prompt: str, state: ExecutionState) -> Tuple[str, bool]:
        """
        Menjalankan tugas agen. Mengembalikan (output_string, success_boolean).
        Mampu memproses pemanggilan tool / function calling secara berurutan.
        """
        messages = [
            Message(role=MessageRole.SYSTEM, content=self.system_prompt),
            Message(role=MessageRole.USER, content=f"Tugas dari Manajer: {task_prompt}")
        ]

        tool_schemas = [t.to_function_definition() for t in self.tools.values()] if self.tools else None

        max_steps = 5
        for step in range(max_steps):
            raw_output = self.llm.generate(messages=messages, tools=tool_schemas)
            
            # Cek apakah LLM menghasilkan tool call (format JSON sederhana atau standard tool call)
            tool_call = self._parse_tool_request(raw_output)
            if tool_call and tool_call["name"] in self.tools:
                tool_name = tool_call["name"]
                args = tool_call.get("args", {})
                
                tool_output = self.tools[tool_name].execute(**args)
                messages.append(Message(role=MessageRole.ASSISTANT, content=f"Mengeksekusi tool {tool_name}..."))
                messages.append(Message(role=MessageRole.TOOL, content=tool_output, name=tool_name))
            else:
                # Selesai eksekusi
                return raw_output, True

        return "Selesai dengan batas maksimal langkah tool.", True

    def _parse_tool_request(self, response_text: str) -> Dict[str, Any]:
        """Menganalisis permintaan tool jika model mengeluarkan blok JSON khusus tool."""
        try:
            if "tool_call:" in response_text or "function:" in response_text:
                start_idx = response_text.find("{")
                end_idx = response_text.rfind("}") + 1
                if start_idx != -1 and end_idx != -1:
                    data = json.loads(response_text[start_idx:end_idx])
                    if "name" in data:
                        return data
        except Exception:
            pass
        return None
