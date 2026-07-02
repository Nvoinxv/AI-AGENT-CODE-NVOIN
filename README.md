# NVOIN AI AGENT CODE (Autonomous Multi-Model Cloud Agent)

**NVOIN AI AGENT CODE** adalah sistem agen otonom berbasis Python & Flutter untuk eksekusi pemrograman profesional, analisis gambar/multimodal, web browsing, dan eksekusi terminal (mendukung penuh **Windows** dan **Linux Arch**).

Sistem ini didesain tanpa ketergantungan model lokal yang memakan banyak penyimpanan disk (seperti Ollama), melainkan memanfaatkan kekuatan **Cloud LLM API** bermutu tinggi:
- **Gemini**: Menggunakan **Gemini 3.5 Flash** (khususnya untuk penulisan kode, eksekusi tool cepat, dan analisis akurat).
- **HuggingFace**: Menggunakan **Gemma 4 31B IT** (`google/gemma-4-31B-it`) untuk nalar mendalam.
- **Qwen**: Menggunakan Qwen DashScope API.

## Arsitektur Nvoin AI (Unified Coding & Orchestration Agent)
Dari sudut pandang pengguna (CLI maupun Frontend Flutter GUI), sistem berfungsi secara cerdas dan otonom. Anda cukup mengirim instruksi pemrograman, mengunggah gambar mockup, atau menyebutkan file/folder lewat antarmuka prompt.

Di balik layar, **Nvoin Manager** bertindak sebagai *Experienced Project Manager*:
1. **Direct Answer**: Menjawab langsung jika instruksi bersifat konseptual atau sederhana dengan latensi ultra-rendah.
2. **Delegation & Execution**: Meminta bantuan agen spesialis internal jika instruksi kompleks:
   - **PlannerAgent**: Merancang Rencana Implementasi dan memecah masalah coding.
   - **CoderAgent**: Menulis dan mengedit berkas kode di sistem berkas secara relatif maupun absolut.
   - **ExecutorAgent**: Menjalankan perintah terminal (PowerShell di Windows, Bash di Arch Linux) serta unit testing.
   - **ReviewerAgent**: Mengaudit keamanan kode, menganalisis gambar/mockup UI, dan melakukan debugging.
3. **Confidence Score & Planning Mode**: Menilai kejelasan instruksi pengguna (0.0 hingga 1.0) untuk mencegah salah eksekusi kode.

---

## 🔬 Evolusi Arsitektur & Efisiensi Penyimpanan
Sesuai analisis di [ARCHITECTURE_ANALYSIS.md](file:///C:/Users/Nvoinvx/Downloads/AI_AGENT_CODE/ARCHITECTURE_ANALYSIS.md):
- **Penghapusan Ollama**: Kami telah menghapus seluruh kontainer dan dependensi Ollama. Hal ini menghemat puluhan gigabyte ruang disk pada komputer Anda sekaligus menghilangkan beban VRAM/RAM lokal.
- **Pembatalan Arsitektur FUGU**: Arsitektur simulasi multi-agen lokal Fugu digantikan oleh **Unified Cloud API Agent** yang langsung menghubungkan Nvoin Manager ke Gemini 3.5 Flash & Gemma 4 31B IT dengan efisiensi dan keakuratan jauh lebih tinggi.

---

## Struktur Proyek

```text
AI_AGENT_CODE/
├── api/                  # Python FastAPI Bridge untuk antarmuka Frontend GUI
├── frontend_ai_agent_code/# Aplikasi Desktop/Web Flutter Nvoin AI
├── core/                 # Logika Inti Nvoin Manager, OS Detection, State, & Message
├── agents/               # Sub-agen spesialis (Planner, Coder, Executor, Reviewer)
├── tools/                # Pustaka alat (File Read/Write, Grep/List, Terminal Runner)
├── models/               # Unified Cloud LLM Client (Gemini, HuggingFace, Qwen)
├── cli/                  # Antarmuka CLI terpadu
├── run_windows.ps1       # Launcher otomatis Windows PowerShell
├── run_windows.bat       # Launcher otomatis Windows CMD
└── run_arch_linux.sh     # Launcher otomatis Arch Linux Bash
```

---

## Panduan Penggunaan Cepat

### 1. Konfigurasi API Key
Salin `.env.example` menjadi `.env` dan masukkan API Key Anda:
```env
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash
GEMINI_API_KEY=your_gemini_key
HUGGING_FACE_API_KEY=your_hf_key
```

### 2. Menjalankan CLI Mode (Terminal)
- **Di Windows**: Jalankan `.\run_windows.ps1` atau `run_windows.bat`
- **Di Arch Linux**: Jalankan `./run_arch_linux.sh`

### 3. Menjalankan Backend API Server & Frontend Flutter
Jalankan server bridge Python:
```bash
python -m api.server
```
Lalu jalankan aplikasi Flutter di folder `frontend_ai_agent_code`:
```bash
cd frontend_ai_agent_code
flutter run -d windows   # Atau -d linux / -d chrome
```
