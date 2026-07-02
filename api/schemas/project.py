from pydantic import BaseModel
from typing import Optional

class ProjectCreateModel(BaseModel):
    name: str
    description: Optional[str] = None
    workspace_path: Optional[str] = "./workspace"
    target_os: Optional[str] = "windows"
    user_id: Optional[str] = "default_user"
