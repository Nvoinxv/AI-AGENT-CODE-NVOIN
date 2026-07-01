from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from core.message import Message

class SubagentResult(BaseModel):
    agent_name: str
    task_prompt: str
    output: str
    success: bool
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ExecutionState(BaseModel):
    """Melacak status, riwayat pesan, dan hasil delegasi manajer Fugu."""
    session_id: str
    messages: List[Message] = Field(default_factory=list)
    subagent_history: List[SubagentResult] = Field(default_factory=list)
    current_loop: int = 0
    is_finished: bool = False
    final_response: Optional[str] = None
    context_variables: Dict[str, Any] = Field(default_factory=dict)

    def add_message(self, message: Message):
        self.messages.append(message)

    def record_subagent_result(self, result: SubagentResult):
        self.subagent_history.append(result)

    def get_summary_for_manager(self) -> str:
        """Merangkum riwayat kerja tim sub-agen untuk dibaca oleh Manajer Fugu."""
        if not self.subagent_history:
            return "Belum ada delegasi tugas ke sub-agen."
        summary = "=== RIWAYAT EKSEKUSI TIM AHLI ===\n"
        for idx, res in enumerate(self.subagent_history, 1):
            status = "SUKSES" if res.success else "GAGAL"
            summary += f"[{idx}] Agen: {res.agent_name} | Status: {status}\n"
            summary += f"    Tugas: {res.task_prompt[:100]}...\n"
            summary += f"    Hasil: {res.output[:250]}...\n\n"
        return summary
