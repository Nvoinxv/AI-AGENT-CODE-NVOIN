import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid

from core.config import get_config
from core.orchestrator import AgentOrchestrator
from core.os_utils import get_os_info
from models.llm_client import LLMClient
from tools.file_tools import ReadFileTool, WriteFileTool
from tools.search_tools import ListDirectoryTool, GrepSearchTool
from tools.terminal_tools import TerminalRunTool
from agents.planner_agent import PlannerAgent
from agents.coder_agent import CoderAgent
from agents.executor_agent import ExecutorAgent
from agents.reviewer_agent import ReviewerAgent

app = FastAPI(title="Nvoin AI Agent Code API Bridge", version="1.0.0")

# Enable CORS untuk Frontend Flutter (Web / Desktop)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator: Optional[AgentOrchestrator] = None

class AttachmentModel(BaseModel):
    type: str  # 'image', 'mention', 'action', 'browser'
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    attachments: Optional[List[AttachmentModel]] = None
    mode: Optional[str] = "fugu_auto"  # 'fugu_auto', 'direct', 'deep_think'

class SubagentLog(BaseModel):
    agent_name: str
    task_prompt: str
    output: str
    success: bool

class ChatResponse(BaseModel):
    session_id: str
    response: str
    subagent_logs: List[SubagentLog]
    os_info: Dict[str, Any]

@app.on_event("startup")
def startup_event():
    global orchestrator
    config = get_config()
    config.agent.workspace_dir.mkdir(parents=True, exist_ok=True)
    llm = LLMClient(config.llm)

    workspace = config.agent.workspace_dir
    shared_tools = [
        ReadFileTool(workspace, allow_outside_workspace=True),
        WriteFileTool(workspace, allow_outside_workspace=True),
        ListDirectoryTool(workspace, allow_outside_workspace=True),
        GrepSearchTool(workspace, allow_outside_workspace=True),
        TerminalRunTool(workspace)
    ]

    agents = {
        "planner": PlannerAgent(llm, tools=shared_tools[:4]),
        "coder": CoderAgent(llm, tools=shared_tools),
        "executor": ExecutorAgent(llm, tools=[ReadFileTool(workspace, allow_outside_workspace=True), TerminalRunTool(workspace)]),
        "reviewer": ReviewerAgent(llm, tools=shared_tools)
    }

    orchestrator = AgentOrchestrator(config, llm, agents)
    print("=== Nvoin AI Backend API Bridge Siap Melayani Frontend ===")

@app.get("/api/v1/status")
def get_status():
    return {
        "status": "online",
        "agent": "Nvoin AI Agent Code",
        "llm_backend": get_config().llm.backend,
        "model_name": get_config().llm.model_name,
        "os_info": get_os_info()
    }

@app.post("/api/v1/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    global orchestrator
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator belum diinisialisasi.")

    session_id = req.session_id or str(uuid.uuid4())[:8]

    # Rakit prompt beserta lampiran multimodal jika ada
    full_prompt = req.prompt
    if req.attachments:
        full_prompt += "\n\n=== LAMPIRAN MULTIMODAL & FITUR TAMBAHAN ==="
        for att in req.attachments:
            full_prompt += f"\n[{att.type.upper()}]: {att.content}"

    # Eksekusi orchestrator Nvoin
    response_text = orchestrator.run(full_prompt, session_id=session_id)

    # Ekstrak riwayat subagent log jika ada dalam state
    # Untuk simulasi API response yang profesional:
    subagent_logs = []
    return ChatResponse(
        session_id=session_id,
        response=response_text,
        subagent_logs=subagent_logs,
        os_info=get_os_info()
    )

@app.get("/api/v1/workspace/files")
def list_workspace_files():
    config = get_config()
    tool = ListDirectoryTool(config.agent.workspace_dir, allow_outside_workspace=True)
    res = tool.execute(".")
    return {"workspace_dir": str(config.agent.workspace_dir), "output": res}

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
