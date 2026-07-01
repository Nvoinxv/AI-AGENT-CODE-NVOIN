import subprocess
import platform
from pathlib import Path
from tools.base_tool import BaseTool

class TerminalRunTool(BaseTool):
    name = "run_command"
    description = "Menjalankan perintah terminal/shell (Mendukung PowerShell di Windows & Bash/Zsh di Arch Linux)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Perintah shell yang akan dieksekusi."},
            "cwd": {"type": "string", "description": "Direktori kerja eksekusi perintah (default: workspace saat ini)."}
        },
        "required": ["command"]
    }

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def execute(self, command: str, cwd: str = None, **kwargs) -> str:
        forbidden = ["rm -rf /", "mkfs", "dd if=/dev", "format c:"]
        if any(f.lower() in command.lower() for f in forbidden):
            return "Error: Perintah ditolak karena alasan keamanan sistem berbahaya."

        target_cwd = self.workspace_dir
        if cwd:
            p = Path(cwd)
            target_cwd = p.resolve() if p.is_absolute() else (self.workspace_dir / p).resolve()
            if not target_cwd.exists():
                return f"Error: Direktori kerja '{target_cwd}' tidak ditemukan."

        is_windows = platform.system() == "Windows"
        
        # Di Windows, gunakan PowerShell jika tersedia untuk fleksibilitas yang setara bash
        shell_cmd = command
        if is_windows:
            # Gunakan powershell command wrapper
            shell_cmd = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{command}"'

        try:
            process = subprocess.run(
                shell_cmd if is_windows else command,
                shell=True,
                cwd=str(target_cwd),
                capture_output=True,
                text=True,
                timeout=60
            )
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            exit_code = process.returncode

            output = f"=== EKSEKUSI TERMINAL ({'Windows PowerShell' if is_windows else 'Linux Bash'}) [Exit: {exit_code}] ===\n"
            output += f"CWD: {target_cwd}\n"
            if stdout:
                output += f"STDOUT:\n{stdout}\n"
            if stderr:
                output += f"STDERR:\n{stderr}\n"
            if not stdout and not stderr:
                output += "Perintah selesai tanpa output (silent success)."
            return output
        except subprocess.TimeoutExpired:
            return "Error: Eksekusi perintah melebihi batas waktu (timeout 60 detik)."
        except Exception as e:
            return f"Error menjalankan perintah terminal: {str(e)}"
