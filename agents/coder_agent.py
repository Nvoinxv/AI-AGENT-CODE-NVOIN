from typing import List
from agents.base_agent import BaseAgent
from models.llm_client import LLMClient
from models.prompts import CODER_PROMPT
from tools.base_tool import BaseTool

class CoderAgent(BaseAgent):
    """Agen Ahli Pemrograman (Coder). Bertanggung jawab menulis dan memodifikasi berkas kode."""
    def __init__(self, llm_client: LLMClient, tools: List[BaseTool] = None):
        super().__init__(
            name="coder",
            system_prompt=CODER_PROMPT,
            llm_client=llm_client,
            tools=tools
        )
