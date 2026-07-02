import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

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
from core.db.postgres import init_postgres

# Re-export schemas demi kompatibilitas ke belakang
from api.schemas.auth import UserRegisterModel, UserLoginModel, PasswordResetModel
from api.schemas.project import ProjectCreateModel
from api.schemas.chat import AttachmentModel, ChatRequest, SubagentLog, ChatResponse

# Import Modular Routers
from api.routers import auth as auth_router
from api.routers import projects as projects_router
from api.routers import chat as chat_router

app = FastAPI(title="Nvoin AI Agent Code API Bridge", version="2.0.0")

# Enable CORS untuk Frontend Flutter (Web / Desktop)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Modular Routers
app.include_router(auth_router.router)
app.include_router(projects_router.router)
app.include_router(chat_router.router)

orchestrator: Optional[AgentOrchestrator] = None

@app.on_event("startup")
def startup_event():
    global orchestrator
    init_postgres()
    config = get_config()
    config.agent.workspace_dir.mkdir(parents=True, exist_ok=True)
    llm = LLMClient(config.llm)

    workspace = config.agent.workspace_dir
    from tools.web_tools import FetchWebPageTool
    shared_tools = [
        ReadFileTool(workspace, allow_outside_workspace=True),
        WriteFileTool(workspace, allow_outside_workspace=True),
        ListDirectoryTool(workspace, allow_outside_workspace=True),
        GrepSearchTool(workspace, allow_outside_workspace=True),
        TerminalRunTool(workspace),
        FetchWebPageTool()
    ]

    agents = {
        "planner": PlannerAgent(llm, tools=shared_tools[:4]),
        "coder": CoderAgent(llm, tools=shared_tools),
        "executor": ExecutorAgent(llm, tools=[ReadFileTool(workspace, allow_outside_workspace=True), TerminalRunTool(workspace)]),
        "reviewer": ReviewerAgent(llm, tools=shared_tools)
    }

    orchestrator = AgentOrchestrator(config, llm, agents)
    chat_router.orchestrator = orchestrator
    print("=== Nvoin AI Backend API Bridge Siap Melayani Frontend ===")

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
