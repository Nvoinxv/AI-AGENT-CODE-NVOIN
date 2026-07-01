from typing import List
from agents.base_agent import BaseAgent
from models.llm_client import LLMClient
from models.prompts import EXECUTOR_PROMPT
from tools.base_tool import BaseTool

class ExecutorAgent(BaseAgent):
    """Agen Ahli Eksekusi (Executor). Menjalankan perintah terminal, unit test, dan memverifikasi log CLI."""
    def __init__(self, llm_client: LLMClient, tools: List[BaseTool] = None):
        super().__init__(
            name="executor",
            system_prompt=EXECUTOR_PROMPT,
            llm_client=llm_client,
            tools=tools
        )
