<#
.SYNOPSIS
    Launcher AI Agent Code khusus lingkungan Windows (PowerShell).
.DESCRIPTION
    Skrip ini memastikan virtual environment Python siap, dependensi terinstal, dan
    variabel lingkungan dikonfigurasi dengan benar di Windows.
#>

$ErrorActionPreference = "Stop"

Write-Host "=== NVOIN AI AGENT CODE - WINDOWS LAUNCHER ===" -ForegroundColor Cyan

# 1. Cek apakah Python terinstal
if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python tidak ditemukan di PATH Windows Anda." -ForegroundColor Red
    Write-Host "Silakan instal Python melalui winget: winget install Python.Python.3.11" -ForegroundColor Yellow
    exit 1
}

# 2. Buat Virtual Environment jika belum ada
$VenvDir = Join-Path $PSScriptRoot ".venv_win"
if (-not (Test-Path $VenvDir)) {
    Write-Host "[1/3] Membuat Python Virtual Environment untuk Windows..." -ForegroundColor Green
    python -m venv $VenvDir
}

# 3. Aktifkan Virtual Environment
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvPip = Join-Path $VenvDir "Scripts\pip.exe"

Write-Host "[2/3] Memeriksa dependensi Python di requirements.txt..." -ForegroundColor Green
& $VenvPip install --quiet --upgrade pip
& $VenvPip install -r (Join-Path $PSScriptRoot "requirements.txt")

# 4. Set Environment Variables default (Jika belum diatur pengguna)
if (-not $env:LLM_PROVIDER) { $env:LLM_PROVIDER = "gemini" }
if (-not $env:LLM_MODEL) { $env:LLM_MODEL = "gemini-3.5-flash" }

Write-Host "[3/3] Menjalankan AI Agent Code CLI (Backend: $env:LLM_PROVIDER | Model: $env:LLM_MODEL)..." -ForegroundColor Green
Write-Host "-----------------------------------------------------------------" -ForegroundColor Gray

& $VenvPython -m cli.main
