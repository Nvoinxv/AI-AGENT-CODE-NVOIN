import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    """Konfigurasi backend LLM untuk Nvoin AI (Mendukung Gemini 3.5 Flash, HuggingFace Gemma 4 31B IT, dan Qwen)."""
    backend: str = Field(default_factory=lambda: os.getenv("LLM_BACKEND", os.getenv("LLM_PROVIDER", "gemini")))
    model_name: str = Field(default_factory=lambda: os.getenv("LLM_MODEL", "gemini-3.5-flash"))
    base_url: str = Field(default_factory=lambda: os.getenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai"))
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=2048)
    api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", os.getenv("HUGGING_FACE_API_KEY", os.getenv("QWEN_MODEL_API", "EMPTY"))))
    max_tokens: int = Field(default=1024)
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
