import os
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class LLMConfig(BaseModel):
    """Konfigurasi backend LLM untuk Fugu Manager dan Sub-Agen (Dioptimalkan untuk RTX 3050 + 8GB RAM)."""
    backend: str = Field(default_factory=lambda: os.getenv("LLM_BACKEND", "ollama"))
    model_name: str = Field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "gemma4:12b"))
    base_url: str = Field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    temperature: float = Field(default=0.2)
    max_tokens: int = Field(default=1024)
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", "EMPTY"))
    
    # Optimasi Komputasi Hardware Ringan (RTX 3050 4GB/8GB & System RAM 8GB)
    num_ctx: int = Field(default=2048, description="Batas konteks memori KV agar tidak membebani RAM 8GB")
    num_predict: int = Field(default=1024, description="Batas keluaran token per giliran untuk mencegah deep thinking berlebih")
    low_vram: bool = Field(default=True, description="Mode hemat VRAM untuk RTX 3050")
    num_gpu: int = Field(default=24, description="Jumlah layer GPU yang di-offload agar tidak CUDA OOM")

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
