from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class AttachmentModel(BaseModel):
    type: str  # 'image', 'mention', 'action', 'browser'
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    prompt: str
    session_id: Optional[str] = None
    project_id: Optional[str] = "default_project"
    user_id: Optional[str] = "default_user"
    attachments: Optional[List[AttachmentModel]] = None
    mode: Optional[str] = "auto"  # 'auto', 'direct', 'deep_think'

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
