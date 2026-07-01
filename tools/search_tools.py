import os
import fnmatch
from pathlib import Path
from tools.base_tool import BaseTool

class ListDirectoryTool(BaseTool):
    name = "list_dir"
    description = "Mendaftar berkas dan direktori di folder relatif workspace atau folder absolut sistem."
    parameters_schema = {
        "type": "object",
        "properties": {
            "subpath": {"type": "string", "description": "Path direktori (contoh: '.' atau 'C:\\Users' atau '/var/log')."}
        }
    }

    def __init__(self, workspace_dir: Path, allow_outside_workspace: bool = True):
        self.workspace_dir = workspace_dir
        self.allow_outside_workspace = allow_outside_workspace

    def execute(self, subpath: str = ".", **kwargs) -> str:
        p = Path(subpath)
        if p.is_absolute():
            target = p.resolve()
        else:
            target = (self.workspace_dir / p).resolve()

        if not self.allow_outside_workspace and not str(target).startswith(str(self.workspace_dir)):
            return "Error: Keamanan akses ditolak."
        if not target.exists() or not target.is_dir():
            return f"Error: Folder '{target}' tidak ditemukan."
        
        items = []
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for f in files:
                if not f.startswith("."):
                    full_path = Path(root) / f
                    try:
                        rel = full_path.relative_to(target)
                        items.append(str(rel))
                    except ValueError:
                        items.append(str(full_path))
        
        if not items:
            return f"Direktori '{target}' kosong."
        return f"=== DAFTAR BERKAS DI: {target} ===\n" + "\n".join(sorted(items)[:100])

class GrepSearchTool(BaseTool):
    name = "grep_search"
    description = "Mencari pola teks dalam berkas-berkas di direktori target (Windows & Arch Linux)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Teks yang ingin dicari."},
            "search_path": {"type": "string", "description": "Folder target pencarian (default: workspace saat ini)."},
            "file_pattern": {"type": "string", "description": "Pola nama berkas (misal: '*.py' atau '*.sh')."}
        },
        "required": ["query"]
    }

    def __init__(self, workspace_dir: Path, allow_outside_workspace: bool = True):
        self.workspace_dir = workspace_dir
        self.allow_outside_workspace = allow_outside_workspace

    def execute(self, query: str, search_path: str = ".", file_pattern: str = "*", **kwargs) -> str:
        p = Path(search_path)
        target_dir = p.resolve() if p.is_absolute() else (self.workspace_dir / p).resolve()

        if not self.allow_outside_workspace and not str(target_dir).startswith(str(self.workspace_dir)):
            return "Error: Keamanan akses ditolak."

        results = []
        for root, dirs, files in os.walk(target_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in fnmatch.filter(files, file_pattern):
                filepath = Path(root) / filename
                for enc in ["utf-8", "utf-8-sig", "cp1252", "latin-1"]:
                    try:
                        with open(filepath, "r", encoding=enc) as f:
                            for idx, line in enumerate(f, 1):
                                if query in line:
                                    try:
                                        rel_path = filepath.relative_to(target_dir)
                                    except ValueError:
                                        rel_path = filepath
                                    results.append(f"{rel_path}:{idx}: {line.strip()}")
                        break
                    except Exception:
                        continue
        if not results:
            return f"Tidak ada hasil pencarian untuk '{query}' di dalam '{target_dir}'."
        return f"=== HASIL GREP ('{query}') DI: {target_dir} ===\n" + "\n".join(results[:50])
