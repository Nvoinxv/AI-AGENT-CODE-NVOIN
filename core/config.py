import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    """Konfigurasi backend LLM untuk Fugu Manager dan Sub-Agen."""
    backend: str = Field(default_factory=lambda: os.getenv("LLM_BACKEND", "ollama"))
    model_name: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "gemma4:12b"))
    base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=4096)
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", "EMPTY"))

class AgentConfig(BaseModel):
    """Konfigurasi sistem untuk AI Agent Code."""
    workspace_dir: Path = Field(default_factory=lambda: Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve())
    max_loops: int = Field(default=10, description="Batas maksimal putaran otomatis (looping/healing)")
    verbose: bool = Field(default=True)
    enable_sandbox: bool = Field(default=True)

class SystemConfig(BaseModel):
    llm: LLMConfig = Field(default_factory=LLMConfig)
    agent: AgentConfig = Field(default_factory=AgentConfig)

def get_config() -> SystemConfig:
    return SystemConfig()
