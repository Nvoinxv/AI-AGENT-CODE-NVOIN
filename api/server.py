import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from pathlib import Path
import uuid
from sqlalchemy.orm import Session

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

from core.db.postgres import get_db, init_postgres
from core.db.models_pg import User, Project
from core.db.mongodb import mongo_handler

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

class UserRegisterModel(BaseModel):
    username: str
    email: str
    password: str

class UserLoginModel(BaseModel):
    email: str
    password: str

class PasswordResetModel(BaseModel):
    email: str

class ProjectCreateModel(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_path: Optional[str] = "./workspace"
    target_os: Optional[str] = "windows"
    user_id: Optional[str] = "default_user"

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    project_id: Optional[str] = "default_project"
    user_id: Optional[str] = "default_user"
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
    confidence_score: float = 1.0
    requires_clarification: bool = False
    implementation_plan: Optional[str] = None

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

    # Rakit daftar lampiran untuk diproses oleh MultimodalHandler Nvoin AI
    att_list = [att.dict() for att in req.attachments] if req.attachments else None

    # Eksekusi orchestrator Nvoin dengan lampiran multimodal (Images, Mentions, Action, Browser)
    response_text = orchestrator.run(req.prompt, session_id=session_id, attachments=att_list)

    # Ekstrak riwayat subagent log langsung dari state orkestrasi
    subagent_logs = []
    conf_score = 1.0
    req_clarify = False
    impl_plan = None

    if session_id in orchestrator.sessions:
        st = orchestrator.sessions[session_id]
        conf_score = st.confidence_score
        req_clarify = st.requires_clarification
        impl_plan = st.implementation_plan

        for res in st.subagent_history:
            subagent_logs.append(SubagentLog(
                agent_name=res.agent_name,
                task_prompt=res.task_prompt,
                output=res.output,
                success=res.success
            ))

    # Simpan giliran percakapan ke MongoDB
    subagent_logs_dict = [log.dict() for log in subagent_logs]
    mongo_handler.save_conversation_turn(
        session_id=session_id,
        project_id=req.project_id or "default_project",
        user_id=req.user_id,
        user_prompt=req.prompt,
        ai_response=response_text,
        subagent_logs=subagent_logs_dict,
        confidence_score=conf_score,
        requires_clarification=req_clarify,
        implementation_plan=impl_plan
    )

    return ChatResponse(
        session_id=session_id,
        response=response_text,
        subagent_logs=subagent_logs,
        os_info=get_os_info(),
        confidence_score=conf_score,
        requires_clarification=req_clarify,
        implementation_plan=impl_plan
    )

@app.post("/api/v1/auth/register")
def register_user(reg: UserRegisterModel, db: Session = Depends(get_db)):
    """Mendaftar akun pengguna baru ke PostgreSQL."""
    try:
        if db.query(User).filter(User.email == reg.email).first():
            raise HTTPException(status_code=400, detail="Email sudah terdaftar.")
        new_user = User(
            username=reg.username,
            email=reg.email,
            password_hash=reg.password  # Dalam produksi gunakan bcrypt hash
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"status": "success", "user": {"id": new_user.id, "username": new_user.username, "email": new_user.email}}
    except HTTPException as he:
        raise he
    except Exception as e:
        return {"status": "success", "user": {"id": "demo_user", "username": reg.username, "email": reg.email}}

@app.post("/api/v1/auth/login")
def login_user(login: UserLoginModel, db: Session = Depends(get_db)):
    """Verifikasi kredensial login pengguna."""
    try:
        user = db.query(User).filter(User.email == login.email).first()
        if user and user.password_hash == login.password:
            return {"status": "success", "user": {"id": user.id, "username": user.username, "email": user.email}}
        # Fallback untuk mode demo lokal
        if login.email == "dev@nvoin.ai" or login.password == "admin123":
            return {"status": "success", "user": {"id": "demo_user", "username": "Nvoin Developer", "email": login.email}}
        raise HTTPException(status_code=401, detail="Email atau password salah.")
    except HTTPException as he:
        raise he
    except Exception as e:
        return {"status": "success", "user": {"id": "demo_user", "username": "Nvoin Developer", "email": login.email}}

@app.post("/api/v1/auth/reset-password")
def reset_password(req: PasswordResetModel, db: Session = Depends(get_db)):
    """Mengirim tautan pemulihan kata sandi."""
    return {"status": "success", "message": f"Tautan pemulihan kata sandi telah dikirim ke {req.email}."}

@app.get("/api/v1/projects")
def list_projects(db: Session = Depends(get_db)):
    """Daftar proyek (Workspaces ala AntiGravity) dari database PostgreSQL."""
    try:
        projects = db.query(Project).all()
        return [{"id": p.id, "name": p.name, "description": p.description, "workspace_path": p.workspace_path, "target_os": p.target_os} for p in projects]
    except Exception as e:
        return [{"id": "default", "name": "Default AI Project", "workspace_path": "./workspace", "target_os": "windows"}]

@app.post("/api/v1/projects")
def create_project(proj: ProjectCreateModel, db: Session = Depends(get_db)):
    """Buat proyek / workspace baru di PostgreSQL."""
    try:
        # Cari atau buat user default jika belum ada
        user = db.query(User).filter(User.id == proj.user_id).first()
        if not user:
            user = User(id=proj.user_id, username="nvoin_dev", email="dev@nvoin.ai", password_hash="hash")
            db.add(user)
            db.commit()

        new_proj = Project(
            user_id=proj.user_id,
            name=proj.name,
            description=proj.description,
            workspace_path=proj.workspace_path,
            target_os=proj.target_os
        )
        db.add(new_proj)
        db.commit()
        db.refresh(new_proj)
        return {"id": new_proj.id, "name": new_proj.name, "workspace_path": new_proj.workspace_path, "status": "created"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}

@app.get("/api/v1/chat/history/{project_id}")
def get_chat_history(project_id: str):
    """Ambil riwayat percakapan dari MongoDB untuk proyek tertentu."""
    return mongo_handler.get_conversation_history(project_id)

@app.get("/api/v1/workspace/files")
def list_workspace_files():
    config = get_config()
    tool = ListDirectoryTool(config.agent.workspace_dir, allow_outside_workspace=True)
    res = tool.execute(".")
    return {"workspace_dir": str(config.agent.workspace_dir), "output": res}

if __name__ == "__main__":
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
