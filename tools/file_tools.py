import os
from pathlib import Path
from tools.base_tool import BaseTool

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Membaca isi berkas teks dari jalur (path) relatif terhadap workspace."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Jalur berkas yang ingin dibaca."}
        },
        "required": ["path"]
    }

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def execute(self, path: str, **kwargs) -> str:
        target = (self.workspace_dir / path).resolve()
        if not str(target).startswith(str(self.workspace_dir)):
            return "Error: Keamanan akses ditolak. Jalur berada di luar ruang kerja (workspace)."
        if not target.exists():
            return f"Error: Berkas '{path}' tidak ditemukan."
        try:
            with open(target, "r", encoding="utf-8") as f:
                content = f.read()
            return f"=== ISI BERKAS: {path} ===\n{content}"
        except Exception as e:
            return f"Error membaca berkas '{path}': {str(e)}"

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Membuat atau menimpa berkas dengan isi baru di dalam workspace."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Jalur berkas tujuan."},
            "content": {"type": "string", "description": "Isi lengkap kode atau teks yang akan ditulis."}
        },
        "required": ["path", "content"]
    }

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def execute(self, path: str, content: str = "", **kwargs) -> str:
        target = (self.workspace_dir / path).resolve()
        if not str(target).startswith(str(self.workspace_dir)):
            return "Error: Keamanan akses ditolak. Jalur berada di luar ruang kerja (workspace)."
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Berhasil menulis isi ke berkas '{path}' ({len(content)} karakter)."
        except Exception as e:
            return f"Error menulis ke berkas '{path}': {str(e)}"
