from typing import List
from agents.base_agent import BaseAgent
from models.llm_client import LLMClient
from models.prompts import REVIEWER_PROMPT
from tools.base_tool import BaseTool

class ReviewerAgent(BaseAgent):
    """Agen Ahli Audit & Review (Reviewer). Mengevaluasi keamanan, celah bug, dan debugging stack trace."""
    def __init__(self, llm_client: LLMClient, tools: List[BaseTool] = None):
        super().__init__(
            name="reviewer",
            system_prompt=REVIEWER_PROMPT,
            llm_client=llm_client,
            tools=tools
        )
