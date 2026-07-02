from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.db.postgres import get_db
from core.db.models_pg import User, Project
from core.config import get_config
from tools.search_tools import ListDirectoryTool
from api.schemas.project import ProjectCreateModel

router = APIRouter(tags=["Projects & Workspace"])

@router.get("/api/v1/projects")
def list_projects(db: Session = Depends(get_db)):
    """Daftar proyek (Workspaces) dari database PostgreSQL."""
    try:
        projects = db.query(Project).all()
        return [{"id": p.id, "name": p.name, "description": p.description, "workspace_path": p.workspace_path, "target_os": p.target_os} for p in projects]
    except Exception:
        return [{"id": "default", "name": "Default AI Project", "workspace_path": "./workspace", "target_os": "windows"}]

@router.post("/api/v1/projects")
def create_project(proj: ProjectCreateModel, db: Session = Depends(get_db)):
    """Buat proyek / workspace baru di PostgreSQL."""
    try:
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

@router.get("/api/v1/workspace/files")
def list_workspace_files():
    config = get_config()
    tool = ListDirectoryTool(config.agent.workspace_dir, allow_outside_workspace=True)
    res = tool.execute(".")
    return {"workspace_dir": str(config.agent.workspace_dir), "output": res}
