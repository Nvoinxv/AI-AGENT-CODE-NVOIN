import json
import uuid
from typing import Dict, Any, List, Optional
from core.config import SystemConfig
from core.message import Message, MessageRole
from core.state import ExecutionState, SubagentResult
from models.llm_client import LLMClient
from models.prompts import FUGU_MANAGER_PROMPT
from core.multimodal_handler import MultimodalHandler

class AgentOrchestrator:
    """
    Inti dari sistem Fugu Architecture.
    Menyajikan antarmuka tunggal seolah-olah 1 model AI, namun di dalam
    bertindak sebagai Project Manager yang mendelegasikan tugas ke tim ahli.
    """
    def __init__(self, config: SystemConfig, llm_client: LLMClient, agents: Dict[str, Any]):
        self.config = config
        self.llm = llm_client
        self.agents = agents  # Dict berisi: 'planner', 'coder', 'executor', 'reviewer'
        self.multimodal_handler = MultimodalHandler(config.agent.workspace_dir)

    def run(self, user_prompt: str, session_id: str = None, attachments: Optional[list] = None) -> str:
        """Entry point utama untuk antarmuka pengguna."""
        if not session_id:
            session_id = str(uuid.uuid4())[:8]

        state = ExecutionState(session_id=session_id)
        
        # 1. Pra-pemrosesan Multimodal & Resolusi Mentions
        enriched_prompt, images_list = self.multimodal_handler.process_input(user_prompt, attachments)
        
        state.add_message(Message(role=MessageRole.USER, content=enriched_prompt, images=images_list))

        print(f"\n[Fugu Orchestrator] Menerima instruksi (Session: {session_id})...")

        while state.current_loop < self.config.agent.max_loops and not state.is_finished:
            state.current_loop += 1
            if self.config.agent.verbose:
                print(f"[Fugu Orchestrator] Iterasi Manajer #{state.current_loop}")

            # 1. Siapkan konteks untuk Manajer
            manager_context = FUGU_MANAGER_PROMPT.format(
                subagent_summary=state.get_summary_for_manager(),
                user_prompt=user_prompt
            )

            messages_for_llm = [
                Message(role=MessageRole.SYSTEM, content=manager_context),
            ] + state.messages

            # 2. Minta Manajer mengambil keputusan (Direct vs Delegate vs Finalize)
            raw_response = self.llm.generate(messages=messages_for_llm, temperature=0.1)
            
            action_plan = self._parse_manager_decision(raw_response)

            if action_plan.get("action") == "direct_answer" or action_plan.get("action") == "finish":
                final_answer = action_plan.get("response", raw_response)
                state.final_response = final_answer
                state.is_finished = True
                state.add_message(Message(role=MessageRole.ASSISTANT, content=final_answer))
                break

            elif action_plan.get("action") == "delegate":
                target_agent = action_plan.get("agent")
                task_prompt = action_plan.get("instruction", user_prompt)

                if target_agent in self.agents:
                    if self.config.agent.verbose:
                        print(f"[Fugu Orchestrator] Mendelegasikan ke Tim Ahli: [{target_agent.upper()}] -> {task_prompt[:60]}...")
                    
                    sub_agent = self.agents[target_agent]
                    agent_output, success = sub_agent.execute(task_prompt, state)
                    
                    state.record_subagent_result(
                        SubagentResult(
                            agent_name=target_agent,
                            task_prompt=task_prompt,
                            output=agent_output,
                            success=success
                        )
                    )
                else:
                    error_msg = f"Error: Agen ahli '{target_agent}' tidak ditemukan dalam tim."
                    state.record_subagent_result(
                        SubagentResult(agent_name=target_agent or "unknown", task_prompt=task_prompt, output=error_msg, success=False)
                    )

        return state.final_response or "Peringatan: Batas maksimal perputaran tercapai tanpa kesimpulan akhir."

    def _parse_manager_decision(self, response_text: str) -> Dict[str, Any]:
        """Mengekstrak blok JSON dari output LLM Manajer."""
        try:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
        except Exception:
            pass
        # Fallback jika model menjawab dalam teks biasa tanpa JSON structured output
        return {"action": "direct_answer", "response": response_text}
