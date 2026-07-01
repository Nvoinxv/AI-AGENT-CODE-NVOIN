import os
import sys
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any

def get_os_info() -> Dict[str, Any]:
    """
    Mendeteksi sistem operasi saat ini (Khususnya membedakan Windows vs Linux Arch)
    serta informasi shell dan package manager yang tersedia.
    """
    system = platform.system()  # 'Windows', 'Linux', 'Darwin'
    release = platform.release()
    version = platform.version()
    machine = platform.machine()

    info = {
        "os_type": system,
        "os_name": system,
        "release": release,
        "machine": machine,
        "shell": "unknown",
        "package_manager": "unknown",
        "path_separator": os.sep,
        "is_windows": system == "Windows",
        "is_arch_linux": False
    }

    if system == "Windows":
        info["os_name"] = f"Windows {release}"
        # Deteksi PowerShell vs CMD
        info["shell"] = "powershell.exe"
        # Deteksi package manager Windows
        if _command_exists("winget"):
            info["package_manager"] = "winget"
        elif _command_exists("choco"):
            info["package_manager"] = "choco"
        else:
            info["package_manager"] = "pip / python"

    elif system == "Linux":
        # Cek apakah Arch Linux (melalui /etc/os-release atau keberadaan pacman)
        os_release_path = Path("/etc/os-release")
        arch_detected = False
        if os_release_path.exists():
            try:
                content = os_release_path.read_text().lower()
                if "arch" in content or "manjaro" in content or "endeavouros" in content:
                    arch_detected = True
            except Exception:
                pass
        
        if _command_exists("pacman") or arch_detected:
            info["is_arch_linux"] = True
            info["os_name"] = "Arch Linux"
            info["package_manager"] = "pacman (atau yay/paru jika tersedia)"
        else:
            info["os_name"] = f"Linux ({release})"

        # Deteksi shell linux
        info["shell"] = os.getenv("SHELL", "/bin/bash")

    return info

def _command_exists(cmd: str) -> bool:
    try:
        if platform.system() == "Windows":
            res = subprocess.run(f"where {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            res = subprocess.run(f"which {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return res.returncode == 0
    except Exception:
        return False

def get_os_context_prompt() -> str:
    """Menghasilkan teks ringkasan OS untuk disisipkan ke prompt sistem AI."""
    info = get_os_info()
    cwd = Path.cwd().resolve()
    
    prompt = f"\n=== KONTEKS SISTEM OPERASI & LINGKUNGAN ===\n"
    prompt += f"Sistem Operasi : {info['os_name']} ({info['machine']})\n"
    prompt += f"Shell Default  : {info['shell']}\n"
    prompt += f"Package Manager: {info['package_manager']}\n"
    prompt += f"Direktori Kerja: {cwd}\n"
    
    if info["is_windows"]:
        prompt += "Catatan Windows: Gunakan sintaks perintah PowerShell atau CMD yang kompatibel dengan Windows. Gunakan path separator '\\' atau '/' (Path Python mendukung keduanya).\n"
    elif info["is_arch_linux"]:
        prompt += "Catatan Arch Linux: Gunakan sintaks shell bash/zsh POSIX standar. Untuk instalasi paket sistem jika diminta, gunakan perintah 'sudo pacman -S <paket>'.\n"
        
    prompt += "===========================================\n"
    return prompt
