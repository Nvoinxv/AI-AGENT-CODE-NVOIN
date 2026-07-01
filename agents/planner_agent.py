from typing import List
from agents.base_agent import BaseAgent
from models.llm_client import LLMClient
from models.prompts import PLANNER_PROMPT
from tools.base_tool import BaseTool

class PlannerAgent(BaseAgent):
    """Agen Ahli Perencana (Planner). Menganalisis struktur dan membuat arsitektur solusi."""
    def __init__(self, llm_client: LLMClient, tools: List[BaseTool] = None):
        super().__init__(
            name="planner",
            system_prompt=PLANNER_PROMPT,
            llm_client=llm_client,
            tools=tools
        )
