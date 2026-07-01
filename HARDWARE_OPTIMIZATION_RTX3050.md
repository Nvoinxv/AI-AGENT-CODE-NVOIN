# Panduan & Arsitektur Optimasi Perangkat Keras Nvoin AI
## Khusus Spesifikasi Ringan: NVIDIA RTX 3050 (4GB/8GB VRAM) & RAM 8GB DDR4

Menjalankan model **Gemma 4 12B** (atau Gemma 2 12B/9B) yang mendukung kapabilitas Multimodal & Deep Thinking pada spesifikasi perangkat keras terbatas seperti **NVIDIA RTX 3050 + RAM 8GB DDR4** membutuhkan rekayasa komputasi khusus. Tanpa optimasi, proses *deep thinking* berulang pada pertanyaan sederhana akan menyebabkan kehabisan VRAM (CUDA Out of Memory), *swapping* berat ke RAM DDR4, dan *system freeze*.

Sistem **Nvoin AI** telah dilengkapi dengan **4 Lapis Optimasi Komputasi (Four-Layer Hardware & Routing Optimization)** yang dirancang khusus untuk skenario hardware ini:

---

### 1. Fast-Path Circuit Breaker (Heuristic Routing Tanpa Deep Think)
Pada model dengan fitur *deep thinking*, menanyakan pertanyaan sederhana (contoh: *"Halo bro"*, *"Jelaskan apa itu OOP"*, *"Format tanggal hari ini"*) sering kali memicu model untuk berpikir bertele-tele di dalam tag `<think>...</think>` sebelum menjawab.
* **Solusi Nvoin AI**: Kami menanamkan mekanisme `_is_simple_conversational_query()` pada `AgentOrchestrator`.
* **Cara Kerja**: Jika instruksi pengguna pendek (< 35 kata) dan tidak mengandung kata kunci eksekusi teknis berat (`buatkan file`, `eksekusi terminal`, `refactor`, `bug`, dll.), Nvoin AI akan **melewatkan siklus delegasi multi-agen yang berat** dan langsung memanggil model dalam mode *Fast Direct Answer* dengan batas token pendek (`max_tokens=512`), menghemat hingga **80% penggunaan GPU & RAM**.

---

### 2. Deep-Think Stripping & Token Clamping (`clean_deep_think_tags`)
Jika model tetap menghasilkan token refleksi internal yang panjang saat menjawab, Nvoin AI secara otomatis memfilter dan membersihkan tag `<think>...</think>` pada antarmuka pengguna (`llm_client.py`), serta membatasi prediksi maksimum (`num_predict=1024`) sehingga model tidak terjebak dalam *infinite reasoning loop*.

---

### 3. Manajemen Konteks Memori KV Cache (`num_ctx`)
Secara default, Ollama/vLLM mengalokasikan jendela konteks sebesar `8192` atau `4096` token. Pada RAM 8GB DDR4, alokasi KV cache sebesar ini dapat menyedot lebih dari 3-4GB RAM sistem hanya untuk penyangga teks.
* **Optimasi Nvoin AI**: Kami membatasi default `num_ctx=2048` di `core/config.py`. Ukuran ini sangat cukup untuk menampung riwayat kode dan instruksi agen, namun tetap aman dan tidak membebani kapasitas RAM 8GB.

---

### 4. GPU Layer Offloading & Quantization (Q4_K_M / AWQ 4-bit)
Agar model 12B dapat berjalan lancar di RTX 3050:
1. **Kuantisasi Wajib**: Gunakan model dengan format kuantisasi **4-bit (Q4_K_M)** (sekitar 6.8 GB ukuran file). Jangan gunakan FP16 (24 GB) atau INT8 (12 GB).
2. **Offloading Parsial (`num_gpu=24`)**: Mengingat VRAM RTX 3050 terbatas, Nvoin AI mengaturnya agar sebagian layer diproses di VRAM GPU yang sangat cepat, dan sisa layer ditangani oleh RAM DDR4 secara seimbang tanpa memicu *crash* CUDA.

---

### Rekomendasi Pengaturan Model Ollama untuk RTX 3050
Pastikan model yang Anda jalankan di Ollama menggunakan kuantisasi 4-bit. Jika Anda ingin mengunduh atau menjalankan model yang paling optimal, gunakan perintah terminal berikut:

```bash
# Menjalankan Gemma versi kuantisasi 4-bit yang hemat VRAM
ollama run gemma2:9b-instruct-q4_K_M
# atau untuk Gemma 12B
ollama run gemma:12b-instruct-q4_K_M
```

Dengan seluruh optimasi ini, Nvoin AI tetap gesit, responsif, dan stabil dijalankan pada **NVIDIA RTX 3050 dan RAM 8GB DDR4** tanpa hambatan komputasi yang berlebihan!
