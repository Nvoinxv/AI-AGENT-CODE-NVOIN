# NVOIN AI AGENT CODE (Multi-Agent & Multimodal Architecture for Gemma 4 12B)

**NVOIN AI** adalah sistem agen otonom berbasis Python & Flutter untuk eksekusi pemrograman profesional, analisis gambar/multimodal, web browsing, dan eksekusi terminal (mendukung penuh **Windows** dan **Linux Arch**).

## Arsitektur Nvoin AI (Masquerade as a Single Model)
Dari sudut pandang pengguna (CLI maupun Frontend Flutter GUI), sistem ini berfungsi dan terasa seperti **satu model AI tunggal yang sangat cerdas**. Anda cukup mengirim instruksi pemrograman, mengunggah gambar mockup, atau menyebutkan file/folder lewat antarmuka prompt.

Di balik layar, model utama (**Nvoin Manager**) yang disiapkan untuk model open source sekelas **Gemma 4 12B** bertindak sebagai *Experienced Project Manager*:
1. **Direct Answer**: Menjawab langsung jika instruksi bersifat konseptual atau sederhana.
2. **Delegation / Dispatch**: Meminta bantuan tim agen spesialis jika instruksi kompleks:
   - **PlannerAgent**: Merancang arsitektur dan memecah masalah coding.
   - **CoderAgent**: Menulis dan mengedit berkas kode di sistem berkas secara relatif maupun absolut.
   - **ExecutorAgent**: Menjalankan perintah terminal (PowerShell di Windows, Bash di Arch Linux) serta unit testing.
   - **ReviewerAgent**: Mengaudit keamanan kode, menganalisis gambar/mockup UI, dan melakukan debugging.
3. **Iterative Self-Correction Loop**: Memperbaiki error eksekusi secara otomatis hingga tuntas.

---

## Struktur Proyek

```text
AI_AGENT_CODE/
├── api/                  # [NEW] Python FastAPI Bridge untuk antarmuka Frontend GUI
├── frontend_ai_agent_code/# [NEW] Aplikasi Desktop/Web Flutter Nvoin AI
├── core/                 # Logika Inti Nvoin Manager, OS Detection, State, & Message
├── agents/               # Sub-agen spesialis (Planner, Coder, Executor, Reviewer)
├── tools/                # Pustaka alat (File Read/Write, Grep/List, Terminal Runner)
├── models/               # Unified LLM Client (Ollama/vLLM/OpenAI) & Prompts
├── training/             # Pipeline QLoRA Fine-tuning khusus model 12B
├── cli/                  # Antarmuka CLI terpadu
├── run_windows.ps1       # Launcher otomatis Windows PowerShell
├── run_windows.bat       # Launcher otomatis Windows CMD
└── run_arch_linux.sh     # Launcher otomatis Arch Linux Bash
```

---

## Panduan Penggunaan Cepat

### 1. Menjalankan CLI Mode (Terminal)
- **Di Windows**: Jalankan `.\run_windows.ps1` atau `run_windows.bat`
- **Di Arch Linux**: Jalankan `./run_arch_linux.sh`

### 2. Menjalankan Backend API Server & Frontend Flutter
Jalankan server bridge Python:
```bash
python -m api.server
```
Lalu jalankan aplikasi Flutter di folder `frontend_ai_agent_code`:
```bash
cd frontend_ai_agent_code
flutter run -d windows   # Atau -d linux / -d chrome
```
