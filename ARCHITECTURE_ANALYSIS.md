# Analisis Kritis & Batasan Arsitektur Nvoin AI (Fugu Approach)

Dokumen ini menyajikan analisis kritis, batasan sistem, serta trade-off arsitektural dari implementasi **Nvoin AI** yang terinspirasi oleh pendekatan *Sakana Fugu*. Analisis ini dibuat agar pengembangan sistem tetap realistis, jujur secara ilmiah, dan modular.

---

## 1. Perbedaan Mendasar: *System Behavior* vs *Training Recipe*

Harus dipahami secara tegas bahwa deskripsi Fugu AI mengenai *dynamic routing*, *delegasi sub-agen*, dan *agregasi jawaban yang menyamar sebagai satu model* adalah deskripsi **behavior sistem (perilaku luar)**, bukan resep pelatihannya.

Hanya dengan menyusun beberapa prompt dan menghubungkan panggilan kelas Python (`PlannerAgent`, `CoderAgent`, `ExecutorAgent`), kita **belum** melatih model utama (seperti Gemma 4 12B) untuk memiliki kemampuan pengambilan keputusan manajerial secara natif.

Kemampuan natif seperti:
- Menilai tingkat kepastian (*confidence score*) secara biologis/kognitif,
- Memutuskan kapan harus menjawab langsung vs memanggil sub-agen tertentu,
- Mengagregasi output bertentangan dari dua sub-agen,
memerlukan **proyek riset pelatihan khusus** yang melibatkan:
1. Dataset trajektori delegasi multi-agen berskala besar (*Multi-Agent Trajectory SFT*).
2. *Preference Tuning* (RLHF / DPO) khusus untuk keputusan routing.
3. Evaluasi tolok ukur (benchmark) interaksi antar-agen.

---

## 2. Peta Jalan Implementasi Jujur: Tahap Saat Ini vs Tahap Riset Masa Depan

Kami membagi arsitektur Nvoin AI menjadi dua fase yang terpisah dengan batas antarmuka (*hook*) yang jelas:

### Fase 1: Tahap Implementasi Saat Ini (Prompt & Rule-Based Orchestration)
Yang telah kita bangun saat ini adalah **Framework Orkestrasi Modular**:
- **Routing**: Digerakkan oleh *prompt-based instruction* (`NVOIN_MANAGER_PROMPT`) dan *rule-based decision logic* di dalam `AgentOrchestrator`.
- **Eksekusi Tool**: Delegasi langsung ke API sistem berkas, terminal CLI (Windows/Arch), dan web browser.
- **Backend Adaptor**: Kompatibel dengan model open-source apa pun via Ollama, vLLM, atau OpenAI-compatible endpoint.

### Fase 2: Tahap Riset Masa Depan (Fine-Tuned Neural Manager)
Karena `AgentOrchestrator` dirancang secara modular, fungsi `_parse_manager_decision()` dan panggilan LLM manajer berfungsi sebagai **Interface / Hook**. Ketika model Gemma 4 12B kelak selesai di-fine-tune menggunakan pipeline `training/train_gemma_lora.py` dengan dataset delegasi, model tersebut dapat **langsung menggantikan** prompt-based router tanpa merubah satu baris pun pada lapisan eksekusi tool maupun UI Frontend Flutter.

---

## 3. Evaluasi Kritis: Apakah Multi-Agent Selalu Tepat untuk Coding?

Dalam konteks *AI Coding Assistant*, pendekatan multi-agen memiliki trade-off nyata yang harus disadari sejak awal:

| Aspek | Risiko Multi-Agent (Manager → Subagent) | Pendekatan Ideal / Solusi Nvoin AI |
| :--- | :--- | :--- |
| **Overhead Komunikasi & Latency** | Setiap delegasi menambah siklus inferensi, melipatgandakan waktu tunggu (*latency*) dan beban memori GPU. | Menerapkan *Direct Answer Check*: Jika tugas sederhana atau konseptual, Manajer menjawab langsung tanpa delegasi. |
| **Fragmentasi Konteks (*Context Loss*)** | Coding membutuhkan presisi absolut pada *line number*, *stack trace error*, dan *full file diff*. Ringkasan antar-agen sering memotong detail krusial ini. | Mempertahankan *Shared Workspace State* & *Direct Tool Calling* agar agen yang mengeksekusi tetap melihat raw file content. |
| **Sifat Sekuensial Debugging** | Loop pemrograman (*Tulis → Run → Error → Fix*) bersifat sangat sekuensial. | Untuk debugging langsung, satu model kuat dengan *tool-calling* berulang lebih stabil daripada pengoperan pesan antar 3 agen. |

---

## 4. Kapan Multi-Agent Lebih Superior?

Pendekatan multi-agen Nvoin AI memberikan keunggulan masif pada tugas-tugas yang **dapat diparalelkan atau dipisahkan domain keahliannya**:
1. **Eksplorasi & Perancangan Proyek Besar (*Research & Planning*)**: Memecah arsitektur baru tanpa mengotori jendela konteks (*context window*) agen penulisan kode.
2. **Analisis UI/UX & Vision Multimodal (*Reviewer / Design Audit*)**: Mengevaluasi gambar mockup UI secara terpisah dan mencocokkannya dengan kode front-end.
3. **Audit Keamanan & Refactoring Paralel**: Memeriksa potensi kerentanan sistem di background saat proses development berjalan.

---

## 5. Rekomendasi & Komitmen Desain Nvoin AI

1. **Transparansi Sistem**: Kami tidak mengklaim model open-source Anda otomatis menjadi "sistem secerdas Fugu" hanya karena memakai framework ini. Kami menyediakan *harness/orchestrator* profesional yang memaksimalkan potensi model open-source saat ini.
2. **Desain Modular**: Memastikan pemisahan tegas antara *LLM Client/Router*, *State/Session Tracker*, *Tools Suite*, dan *Presentation GUI (Flutter)*.
3. **Kendali Biaya & Latency**: Menghadirkan *Skor Keyakinan (Confidence Score)* dan *Planning Mode* agar sistem tidak membuang-buang token inferensi untuk eksekusi yang salah sasaran.
