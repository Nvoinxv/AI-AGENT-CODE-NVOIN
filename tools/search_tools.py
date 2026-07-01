import os
import fnmatch
from pathlib import Path
from tools.base_tool import BaseTool

class ListDirectoryTool(BaseTool):
    name = "list_dir"
    description = "Mendaftar berkas dan direktori di dalam folder workspace."
    parameters_schema = {
        "type": "object",
        "properties": {
            "subpath": {"type": "string", "description": "Sub-direktori relatif terhadap workspace (default: '.')."}
        }
    }

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def execute(self, subpath: str = ".", **kwargs) -> str:
        target = (self.workspace_dir / subpath).resolve()
        if not str(target).startswith(str(self.workspace_dir)):
            return "Error: Keamanan akses ditolak."
        if not target.exists() or not target.is_dir():
            return f"Error: Folder '{subpath}' tidak ditemukan."
        
        items = []
        for root, dirs, files in os.walk(target):
            # Exclude hidden files / git
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            rel_root = os.path.relpath(root, self.workspace_dir)
            for f in files:
                if not f.startswith("."):
                    items.append(os.path.join(rel_root if rel_root != "." else "", f))
        
        if not items:
            return "Direktori kosong."
        return "=== DAFTAR BERKAS WORKSPACE ===\n" + "\n".join(sorted(items)[:100])

class GrepSearchTool(BaseTool):
    name = "grep_search"
    description = "Mencari kemunculan teks atau pola dalam berkas-berkas kode di workspace."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Teks yang ingin dicari."},
            "file_pattern": {"type": "string", "description": "Pola nama berkas (misal: '*.py')."}
        },
        "required": ["query"]
    }

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def execute(self, query: str, file_pattern: str = "*", **kwargs) -> str:
        results = []
        for root, dirs, files in os.walk(self.workspace_dir):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for filename in fnmatch.filter(files, file_pattern):
                filepath = Path(root) / filename
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        for idx, line in enumerate(f, 1):
                            if query in line:
                                rel_path = filepath.relative_to(self.workspace_dir)
                                results.append(f"{rel_path}:{idx}: {line.strip()}")
                except Exception:
                    continue
        if not results:
            return f"Tidak ada hasil pencarian untuk '{query}'."
        return "=== HASIL PENCARIAN GREP ===\n" + "\n".join(results[:50])
