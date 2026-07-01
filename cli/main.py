import sys
import uuid
from pathlib import Path

from core.config import get_config
from core.orchestrator import AgentOrchestrator
from models.llm_client import LLMClient
from tools.file_tools import ReadFileTool, WriteFileTool
from tools.search_tools import ListDirectoryTool, GrepSearchTool
from tools.terminal_tools import TerminalRunTool

from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.executor_agent import ExecutorAgent
from agents.reviewer_agent import ReviewerAgent

def bootstrap_agent_code() -> AgentOrchestrator:
    config = get_config()
    config.agent.workspace_dir.mkdir(parents=True, exist_ok=True)

    llm = LLMClient(config.llm)

    # Siapkan tools untuk sub-agen
    workspace = config.agent.workspace_dir
    shared_tools = [
        ReadFileTool(workspace),
        WriteFileTool(workspace),
        ListDirectoryTool(workspace),
        GrepSearchTool(workspace),
        TerminalRunTool(workspace)
    ]

    # Buat tim sub-agen spesialis
    agents = {
        "planner": PlannerAgent(llm, tools=shared_tools[:4]), # Planner tidak butuh run terminal
        "coder": CoderAgent(llm, tools=shared_tools),
        "executor": ExecutorAgent(llm, tools=[ReadFileTool(workspace), TerminalRunTool(workspace)]),
        "reviewer": ReviewerAgent(llm, tools=shared_tools)
    }

    orchestrator = AgentOrchestrator(config, llm, agents)
    return orchestrator

def main():
    print("=================================================================")
    print("      AI AGENT CODE (Fugu Architecture - Open Source LLM)        ")
    print("=================================================================")
    print("Masquerade as a single model: Dari luar terlihat seperti 1 AI.")
    print("Ketik 'exit' atau 'quit' untuk mengakhiri sesi.\n")

    orchestrator = bootstrap_agent_code()
    session_id = str(uuid.uuid4())[:8]

    while True:
        try:
            user_input = input("\n[Pengguna] > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Sampai jumpa!")
                break

            response = orchestrator.run(user_input, session_id=session_id)
            print(f"\n[AI Agent Code] >>>\n{response}")

        except KeyboardInterrupt:
            print("\nSesi dihentikan oleh pengguna.")
            break
        except Exception as e:
            print(f"\n[Error Sistem] {str(e)}")

if __name__ == "__main__":
    main()
