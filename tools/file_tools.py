import os
from pathlib import Path
from tools.base_tool import BaseTool

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Membaca isi berkas teks dari jalur relatif (terhadap workspace) atau jalur absolut sistem."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Jalur berkas (contoh Windows: 'C:\\Users\\file.py' atau 'src/main.py'. Contoh Arch Linux: '/home/user/file.py' atau 'src/main.py')."}
        },
        "required": ["path"]
    }

    def __init__(self, workspace_dir: Path, allow_outside_workspace: bool = True):
        self.workspace_dir = workspace_dir
        self.allow_outside_workspace = allow_outside_workspace

    def execute(self, path: str, **kwargs) -> str:
        p = Path(path)
        if p.is_absolute():
            target = p.resolve()
        else:
            target = (self.workspace_dir / p).resolve()

        if not self.allow_outside_workspace and not str(target).startswith(str(self.workspace_dir)):
            return "Error: Keamanan akses ditolak. Jalur berada di luar ruang kerja."
            
        if not target.exists():
            return f"Error: Berkas '{target}' tidak ditemukan."
            
        # Coba baca dengan beberapa encoding populer (mendukung Windows & Linux)
        for enc in ["utf-8", "utf-8-sig", "cp1252", "latin-1"]:
            try:
                with open(target, "r", encoding=enc) as f:
                    content = f.read()
                return f"=== ISI BERKAS: {target} ===\n{content}"
            except UnicodeDecodeError:
                continue
            except Exception as e:
                return f"Error membaca berkas '{target}': {str(e)}"
                
        return f"Error: Berkas '{target}' merupakan berkas biner atau tidak dapat dibaca teksnya."

class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Membuat atau menimpa berkas di jalur relatif atau absolut sistem (Windows & Linux)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Jalur tujuan berkas."},
            "content": {"type": "string", "description": "Isi lengkap kode atau teks yang akan ditulis."}
        },
        "required": ["path", "content"]
    }

    def __init__(self, workspace_dir: Path, allow_outside_workspace: bool = True):
        self.workspace_dir = workspace_dir
        self.allow_outside_workspace = allow_outside_workspace

    def execute(self, path: str, content: str = "", **kwargs) -> str:
        p = Path(path)
        if p.is_absolute():
            target = p.resolve()
        else:
            target = (self.workspace_dir / p).resolve()

        if not self.allow_outside_workspace and not str(target).startswith(str(self.workspace_dir)):
            return "Error: Keamanan akses ditolak. Jalur berada di luar ruang kerja."
            
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Berhasil menulis isi ke berkas '{target}' ({len(content)} karakter)."
        except Exception as e:
            return f"Error menulis ke berkas '{target}': {str(e)}"
