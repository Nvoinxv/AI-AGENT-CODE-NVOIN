@echo off
TITLE AI AGENT CODE - WINDOWS LAUNCHER
echo === NVOIN AI AGENT CODE - WINDOWS CMD LAUNCHER ===

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python tidak ditemukan di PATH Windows.
    echo Silakan instal Python terlebih dahulu atau gunakan perintah: winget install Python.Python.3.11
    pause
    exit /b 1
)

set VENV_DIR=%~dp0.venv_win
if not exist "%VENV_DIR%" (
    echo [1/3] Membuat Virtual Environment Python Windows...
    python -m venv "%VENV_DIR%"
)

set VENV_PYTHON="%VENV_DIR%\Scripts\python.exe"
set VENV_PIP="%VENV_DIR%\Scripts\pip.exe"

echo [2/3] Menginstal / memperbarui dependensi Python...
%VENV_PIP% install --quiet --upgrade pip
%VENV_PIP% install -r "%~dp0requirements.txt"

if not defined LLM_PROVIDER set LLM_PROVIDER=gemini
if not defined LLM_MODEL set LLM_MODEL=gemini-3.5-flash

echo [3/3] Memulai AI Agent CLI (Backend: %LLM_PROVIDER% | Model: %LLM_MODEL%)...
echo -----------------------------------------------------------------
%VENV_PYTHON% -m cli.main
pause
