import subprocess
from pathlib import Path
from tools.base_tool import BaseTool

class TerminalRunTool(BaseTool):
    name = "run_command"
    description = "Menjalankan perintah terminal/shell di dalam folder workspace (misal: pytest, python script.py)."
    parameters_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Perintah shell yang akan dieksekusi."}
        },
        "required": ["command"]
    }

    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir

    def execute(self, command: str, **kwargs) -> str:
        forbidden = ["rm -rf /", "mkfs", "shutdown", "reboot"]
        if any(f in command for f in forbidden):
            return "Error: Perintah ditolak karena alasan keamanan sistem."

        try:
            process = subprocess.run(
                command,
                shell=True,
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=30
            )
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()
            exit_code = process.returncode

            output = f"=== EKSEKUSI TERMINAL (Exit Code: {exit_code}) ===\n"
            if stdout:
                output += f"STDOUT:\n{stdout}\n"
            if stderr:
                output += f"STDERR:\n{stderr}\n"
            if not stdout and not stderr:
                output += "Perintah selesai tanpa output (silent success)."
            return output
        except subprocess.TimeoutExpired:
            return "Error: Eksekusi perintah melebihi batas waktu (timeout 30 detik)."
        except Exception as e:
            return f"Error menjalankan perintah terminal: {str(e)}"
