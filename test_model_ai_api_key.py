import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

def test_huggingface_models():
    print("\n=======================================================")
    print("PENGUJIAN MODEL GEMMA PADA HUGGING FACE ROUTER API")
    print("=======================================================")
    
    hf_key = os.getenv("HUGGING_FACE_API_KEY")
    if not hf_key:
        print("[X] Error: HUGGING_FACE_API_KEY tidak ditemukan di file .env")
        return

    print(f"[*] API Key terdeteksi : {hf_key[:8]}...{hf_key[-4:]}")
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {hf_key}",
        "Content-Type": "application/json"
    }

    # Model yang ditanyakan user (gemma-2-9b-it) vs Model generasi terbaru yang aktif di HF
    models_to_test = [
        ("google/gemma-2-9b-it", "Model yang kamu tanyakan (Gemma 2)"),
        ("google/gemma-3-12b-it", "Rekomendasi Terbaik (12B - Setara kelas 12B dengan arsitektur Gemma 3)"),
        ("google/gemma-4-26B-A4B-it", "Rekomendasi Gemma 4 (MoE Hemat Komputasi)"),
        ("google/gemma-4-31B-it", "Rekomendasi Gemma 4 (Kapasitas Maksimal)")
    ]

    for model_id, desc in models_to_test:
        print(f"\n-------------------------------------------------------")
        print(f"[*] Menguji : {model_id}")
        print(f"    Keterangan: {desc}")
        payload = {
            "model": model_id,
            "messages": [
                {"role": "user", "content": "Halo Nvoin AI! Sapa dalam 1 kalimat bahasa Indonesia."}
            ],
            "max_tokens": 100,
            "temperature": 0.3
        }
        try:
            with httpx.Client(timeout=35.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"].get("content", "")
                    print(f"    [V] SUKSES! Respons dari model:")
                    print(f"        \"{content.strip()}\"")
                else:
                    err = res.json().get("error", {}).get("message", res.text) if "json" in res.headers.get("content-type", "") else res.text
                    print(f"    [!] Status {res.status_code}: {err[:120]}...")
                    if model_id == "google/gemma-2-9b-it":
                        print(f"        👉 Catatan: Hugging Face Serverless Router telah meningkatkan node Gemma 2 ke varian Gemma 3 & Gemma 4.")
        except Exception as e:
            print(f"    [X] Exception: {str(e)}")

if __name__ == "__main__":
    test_huggingface_models()
