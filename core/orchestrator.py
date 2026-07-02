import json
import uuid
from typing import Dict, Any, List, Optional
from core.config import SystemConfig
from core.message import Message, MessageRole
from core.state import ExecutionState, SubagentResult
from models.llm_client import LLMClient
from models.prompts import NVOIN_MANAGER_PROMPT
from core.multimodal_handler import MultimodalHandler

class AgentOrchestrator:
    """
    Inti dari sistem Nvoin AI Agent Code.
    Menyajikan antarmuka otonom yang memimpin tim ahli pemecahan masalah programming.
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

        print(f"\n[Nvoin Orchestrator] Menerima instruksi (Session: {session_id})...")

        # FAST-PATH CIRCUIT BREAKER:
        # Jika instruksi berupa pertanyaan sederhana, percakapan umum, atau sapaan singkat,
        # jawab langsung tanpa memuat siklus orkestrasi penuh.
        if self._is_simple_conversational_query(user_prompt, attachments):
            if self.config.agent.verbose:
                print("[Nvoin Fast-Path] Menjawab langsung pertanyaan sederhana.")
            fast_messages = [
                Message(role=MessageRole.SYSTEM, content="Anda adalah Nvoin AI. Jawablah pertanyaan atau sapaan pengguna secara singkat, akurat, dan langsung ke intinya."),
                Message(role=MessageRole.USER, content=user_prompt)
            ]
            direct_ans = self.llm.generate(messages=fast_messages, temperature=0.3)
            state.final_response = direct_ans
            state.is_finished = True
            return direct_ans

        while state.current_loop < self.config.agent.max_loops and not state.is_finished:
            state.current_loop += 1
            if self.config.agent.verbose:
                print(f"[Nvoin Orchestrator] Iterasi Manajer #{state.current_loop}")

            # 1. Siapkan konteks untuk Manajer Nvoin AI
            manager_context = NVOIN_MANAGER_PROMPT.format(
                subagent_summary=state.get_summary_for_manager(),
                user_prompt=user_prompt,
                attachments_summary=str(attachments or "Tidak ada lampiran tambahan")
            )

            messages_for_llm = [
                Message(role=MessageRole.SYSTEM, content=manager_context),
            ] + state.messages

            # 2. Minta Manajer mengambil keputusan
            raw_response = self.llm.generate(messages=messages_for_llm, temperature=0.1)
            action_plan = self._parse_manager_decision(raw_response)

            # Simpan skor keyakinan
            if "confidence_score" in action_plan:
                try:
                    state.confidence_score = float(action_plan["confidence_score"])
                except Exception:
                    state.confidence_score = 0.8

            action = action_plan.get("action")

            # AKSI 1: Minta Klarifikasi jika instruksi ambigu (Confidence < 0.75)
            if action == "ask_clarification" or state.confidence_score < 0.75:
                state.requires_clarification = True
                questions = action_plan.get("questions", ["Mohon perjelas detail instruksi Anda."])
                recs = action_plan.get("recommendations", "")
                
                clarification_msg = f"=== [PERINGATAN KEYAKINAN NVOIN AI: {int(state.confidence_score * 100)}%] ===\n"
                clarification_msg += "Instruksi terdeteksi kurang spesifik atau berisiko eksekusi salah. Untuk menghindari kesalahan:\n\n"
                for idx, q in enumerate(questions, 1):
                    clarification_msg += f"{idx}. {q}\n"
                if recs:
                    clarification_msg += f"\n💡 Saran Implementasi Nvoin AI: {recs}\n"
                clarification_msg += "\nSilakan jawab pertanyaan di atas atau konfirmasi agar kami dapat membuatkan Rencana Implementasi."
                
                state.final_response = clarification_msg
                state.is_finished = True
                state.add_message(Message(role=MessageRole.ASSISTANT, content=clarification_msg))
                break

            # AKSI 2: Usulkan Rencana Implementasi (Planning Mode) sebelum eksekusi kode
            elif action == "propose_plan":
                task_prompt = action_plan.get("instruction", "Buat rencana implementasi detail.")
                if "planner" in self.agents:
                    plan_output, _ = self.agents["planner"].execute(task_prompt, state)
                    state.implementation_plan = plan_output
                    
                    plan_msg = f"=== RENCANA IMPLEMENTASI NVOIN AI (Confidence: {int(state.confidence_score * 100)}%) ===\n"
                    plan_msg += plan_output + "\n\n"
                    plan_msg += "❓ Apakah Anda menyetujui Rencana Implementasi di atas sebelum kami mengeksekusi penulisan kode?"
                    
                    state.final_response = plan_msg
                    state.is_finished = True
                    state.add_message(Message(role=MessageRole.ASSISTANT, content=plan_msg))
                    break

            # AKSI 3: Jawab langsung atau selesai
            elif action == "direct_answer" or action == "finish":
                final_answer = action_plan.get("response", raw_response)
                state.final_response = final_answer
                state.is_finished = True
                state.add_message(Message(role=MessageRole.ASSISTANT, content=final_answer))
                break

            # AKSI 4: Delegasikan ke Sub-Agen Eksekusi (Coder / Executor / Reviewer)
            elif action == "delegate":
                target_agent = action_plan.get("agent")
                task_prompt = action_plan.get("instruction", user_prompt)

                if target_agent in self.agents:
                    if self.config.agent.verbose:
                        print(f"[Nvoin Orchestrator] Mendelegasikan ke Tim Ahli: [{target_agent.upper()}] -> {task_prompt[:60]}...")
                    
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
        return {"action": "direct_answer", "response": response_text}

    def _is_simple_conversational_query(self, prompt: str, attachments: Optional[list]) -> bool:
        """Klasifikasi cepat apakah permintaan merupakan sapaan/pertanyaan umum yang sederhana."""
        if attachments and len(attachments) > 0:
            return False

        text_lower = prompt.lower().strip()
        words = text_lower.split()
        
        complex_keywords = [
            'file', 'folder', 'buatkan', 'tulis', 'kode', 'code', 'script', 'eksekusi',
            'run', 'terminal', 'bug', 'debug', 'error', 'refactor', 'scrape', 'browser',
            'install', 'git', 'project', 'proyek', 'docker', 'database', 'sql', 'test', 'struktur'
        ]

        if any(kw in text_lower for kw in complex_keywords):
            return False

        if len(words) < 35:
            return True

        return False
