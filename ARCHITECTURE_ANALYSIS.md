# Analisis Kritis & Evolusi Arsitektur Nvoin AI (Cloud API Migration)

Dokumen ini menyajikan analisis kritis, batasan sistem, serta keputusan evolusi arsitektur dari implementasi **Nvoin AI Agent Code**.

---

## 1. Pembatalan Pendekatan Fugu & Penghapusan Ollama

Pada iterasi awal, sempat dipertimbangkan penggunaan arsitektur simulasi multi-agen lokal bergaya *Sakana Fugu* berbasis model lokal (seperti Gemma 4 12B via Ollama). Namun, setelah evaluasi engineering mendalam, pendekatan tersebut dibatalkan dengan alasan kritis berikut:

1. **Konsumsi Ruang Penyimpanan Disk yang Masif**: Menjalankan model lokal sekelas 12B hingga 31B membutuhkan puluhan gigabyte penyimpanan disk dan memori RAM/VRAM yang berat.
2. **Overhead Komunikasi Multi-Agen Lokal**: Membagi tugas pemrograman sederhana ke dalam banyak loop delegasi agen lokal menimbulkan latensi tinggi serta pemotongan detail krusial (*context loss* pada line number & stack trace).

Sebagai solusinya, Nvoin AI Agent Code beralih sepenuhnya ke **Cloud LLM API**:
- **Gemini 3.5 Flash**: Menjadi mesin utama (*primary engine*) untuk coding dan penulisan berkas karena kecepatan inferensi ultra-tinggi dan pemahaman konteks kode yang kuat.
- **HuggingFace Gemma 4 31B IT**: Disediakan untuk penalaran terbuka berkapasitas maksimal.
- **Qwen**: Mendukung eksekusi kode multi-bahasa melalui DashScope API.

---

## 2. Peta Jalan Implementasi: Unified Cloud Orchestration

Kami menyusun Nvoin AI sebagai **Framework Orkestrasi Otonom Terpadu**:
- **Fast-Path Circuit Breaker**: Jika instruksi bersifat percakapan umum atau pertanyaan singkat, Nvoin Manager langsung menjawab tanpa memuat siklus orkestrasi penuh.
- **Planning Mode & Confidence Score**: Sebelum melakukan penulisan/penghapusan kode di sistem berkas, agen menilai tingkat kepastian (`confidence_score`). Jika di bawah 0.75, sistem meminta klarifikasi. Jika membutuhkan restrukturisasi, agen mengajukan *Implementation Plan*.
- **Eksekusi Tool Langsung**: Delegasi eksekusi langsung ke API sistem berkas absolut/relatif, terminal CLI (PowerShell di Windows / Bash di Arch Linux), dan web browser.

---

## 3. Keunggulan Arsitektur Baru

| Aspek | Arsitektur Fugu Lokal (Ollama) | Arsitektur Baru Nvoin AI (Cloud API) |
| :--- | :--- | :--- |
| **Beban Penyimpanan Disk** | Sangat Berat (Puluhan GB untuk bobot model lokal). | **Sangat Ringan (0 GB untuk bobot model)**. |
| **Kebutuhan Hardware (VRAM/RAM)** | Membutuhkan GPU dedicated minimal 8GB-16GB VRAM. | **Ringan**, dapat berjalan di laptop/komputer standar apa pun. |
| **Kecepatan Coding & Presisi** | Terbatas oleh kapasitas model 12B lokal & latensi multi-loop. | **Presisi Tinggi** menggunakan **Gemini 3.5 Flash** & **Gemma 4 31B IT**. |

---

## 4. Komitmen Desain Nvoin AI

1. **Efisiensi Sumber Daya**: Menghapus seluruh dependensi lokal yang tidak terpakai, termasuk folder pelatihan (*training*) dan engine Ollama lokal.
2. **Desain Modular**: Memastikan pemisahan tegas antara *LLM Client/Router*, *State/Session Tracker*, *Tools Suite*, dan *Presentation GUI (Flutter)*.
3. **Keamanan Eksekusi**: Menghadirkan *Skor Keyakinan (Confidence Score)* agar eksekusi perintah terminal atau modifikasi kode selalu terkendali dan disetujui pengguna.
