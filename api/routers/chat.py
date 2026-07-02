import uuid
from typing import Optional
from fastapi import APIRouter, HTTPException
from core.config import get_config
from core.os_utils import get_os_info
from core.orchestrator import AgentOrchestrator
from core.db.mongodb import mongo_handler
from api.schemas.chat import ChatRequest, ChatResponse, SubagentLog

router = APIRouter(tags=["Chat & System Status"])

# Global orchestrator instance yang diinisialisasi saat server startup
orchestrator: Optional[AgentOrchestrator] = None

@router.get("/api/v1/status")
def get_status():
    config = get_config()
    return {
        "status": "online",
        "agent": "Nvoin AI Agent Code",
        "llm_backend": config.llm.backend,
        "model_name": config.llm.model_name,
        "os_info": get_os_info()
    }

@router.post("/api/v1/chat", response_model=ChatResponse)
def handle_chat(req: ChatRequest):
    global orchestrator
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Orchestrator belum diinisialisasi.")

    session_id = req.session_id or str(uuid.uuid4())[:8]
    att_list = [att.dict() for att in req.attachments] if req.attachments else None

    if req.mode == 'direct':
        from core.message import Message, MessageRole
        fast_msg = [
            Message(role=MessageRole.SYSTEM, content="Anda adalah Nvoin AI (Fast Direct Mode). Jawablah secara langsung, cepat, ringkas, dan akurat tanpa deep thinking berlebihan atau tag <think>."),
            Message(role=MessageRole.USER, content=req.prompt)
        ]
        response_text = orchestrator.llm.generate(fast_msg, temperature=0.3)
    else:
        response_text = orchestrator.run(req.prompt, session_id=session_id, attachments=att_list)

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

@router.get("/api/v1/chat/history/{project_id}")
def get_chat_history(project_id: str):
    """Ambil riwayat percakapan dari MongoDB untuk proyek tertentu."""
    return mongo_handler.get_conversation_history(project_id)
