# AI AGENT CODE (Fugu Architecture for Gemma 4 12B)

**AI AGENT CODE** adalah sistem agen otonom berbasis Python untuk eksekusi pemrograman (seperti Claude Code atau AntiGravity) yang menggunakan arsitektur orkestrasi multi-agen terinspirasi dari **Sakana Fugu**.

## Arsitektur Fugu AI (Masquerade as a Single Model)
Dari sudut pandang pengguna (CLI / API), sistem ini berfungsi dan terasa seperti **satu model AI tunggal**. Anda hanya cukup mengirim instruksi pemecahan masalah atau pembuatan fitur lewat satu antarmuka prompt.

Di balik layar, model utama (**Fugu Manager**) yang dilatih khusus (misalnya fine-tuning pada **Gemma 4 12B**) bertindak sebagai *Experienced Project Manager*:
1. **Direct Answer**: Menjawab langsung jika instruksi bersifat konseptual atau sederhana.
2. **Delegation / Dispatch**: Meminta bantuan tim agen spesialis jika instruksi kompleks:
   - **PlannerAgent**: Merancang struktur, memecah masalah, dan membuat rencana implementasi.
   - **CoderAgent**: Menulis, mengedit, dan memodifikasi kode program di sistem berkas.
   - **ExecutorAgent**: Menjalankan perintah terminal, pengujian unit (unit test), dan menangkap log output/error.
   - **ReviewerAgent**: Mengaudit keamanan kode, kualitas eksekusi, dan menganalisis kesalahan (debugging).
3. **Iterative Self-Correction Loop**: Jika eksekusi gagal atau mengalami error di terminal, Manajer secara otomatis memanggil ulang agen terkait untuk memperbaiki kesalahan hingga tuntas.

---

## Struktur Direktori

```text
AI_AGENT_CODE/
├── core/             # Logika inti Manajer Orkestrator Fugu, State, & Message
├── agents/           # Sub-agen spesialis (Planner, Coder, Executor, Reviewer)
├── tools/            # Pustaka fungsionalitas (File Tools, Search Tools, Terminal Runner)
├── models/           # Unified LLM Client (vLLM, Ollama, OpenAI-compatible) & Prompts
├── training/         # Pipeline pembuat dataset sintetik & QLoRA Fine-tuning Gemma 12B
├── cli/              # Antarmuka interaktif CLI terpadu
└── requirements.txt  # Daftar dependensi Python
```

---

## Panduan Penggunaan

### 1. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Environment Variable
Buat berkas `.env` atau atur variabel lingkungan untuk endpoint LLM open-source Anda (misalnya Ollama lokal atau vLLM):
```bash
LLM_BACKEND=ollama
OLLAMA_MODEL=gemma4:12b
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Menjalankan CLI Agent
```bash
python -m cli.main
```

---

## Pelatihan Khusus Model Manajer (Gemma 4 12B)

Untuk melatih model open-source agar jago menjadi "Manajer Fugu" (memahami kapan harus menjawab langsung, mendelegasikan ke sub-agen, atau mengulang eksekusi), gunakan pipeline di folder `training/`:

1. **Generate Dataset Sintetik**:
   ```bash
   python -m training.dataset_generator --output data/synthetic_fugu_trajectories.json
   ```
2. **Format Dataset ke ShareGPT/SFT**:
   ```bash
   python -m training.format_dataset --input data/synthetic_fugu_trajectories.json --output data/gemma_sft.jsonl
   ```
3. **Jalankan QLoRA Fine-Tuning**:
   ```bash
   python -m training.train_gemma_lora --dataset data/gemma_sft.jsonl --model_name google/gemma-4-12b
   ```
