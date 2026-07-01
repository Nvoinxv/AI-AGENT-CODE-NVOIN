#!/usr/bin/env bash
# ==============================================================================
# Launcher AI Agent Code Khusus Arch Linux (Fugu Architecture)
# ==============================================================================

set -e

echo -e "\033[1;36m=== AI AGENT CODE (FUGU ARCHITECTURE) - ARCH LINUX LAUNCHER ===\033[0m"

# 1. Cek apakah ini sistem berbasis Arch Linux
if [ -f "/etc/os-release" ]; then
    if grep -iqE "arch|manjaro|endeavour" /etc/os-release; then
        echo -e "\033[1;32m[+] Sistem Arch Linux terdeteksi.\033[0m"
    fi
fi

# 2. Cek paket dasar Arch Linux (python, pip, git, base-devel)
if ! command -v python >/dev/null 2>&1; then
    echo -e "\033[1;31m[!] Python tidak ditemukan. Menginstal via pacman...\033[0m"
    sudo pacman -S --needed python python-pip git base-devel
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv_arch"

# 3. Setup Virtual Environment agar tidak mengganggu paket sistem pacman
if [ ! -d "$VENV_DIR" ]; then
    echo -e "\033[1;33m[1/3] Membuat Virtual Environment Python khusus Arch Linux...\033[0m"
    python -m venv "$VENV_DIR"
fi

VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

# 4. Instal dependensi
echo -e "\033[1;32m[2/3] Memeriksa dependensi di requirements.txt...\033[0m"
$VENV_PIP install --quiet --upgrade pip
$VENV_PIP install -r "$SCRIPT_DIR/requirements.txt"

# 5. Konfigurasi Environment Variables (Dapat dioverride dengan export)
export LLM_BACKEND="${LLM_BACKEND:-ollama}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-gemma4:12b}"
export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"

echo -e "\033[1;32m[3/3] Menjalankan AI Agent Code CLI (Backend: $LLM_BACKEND | Model: $OLLAMA_MODEL)...\033[0m"
echo "-----------------------------------------------------------------"

exec $VENV_PYTHON -m cli.main "$@"
