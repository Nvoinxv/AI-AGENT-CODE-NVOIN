import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

def test_cloud_models():
    print("\n=======================================================")
    print("PENGUJIAN MODEL CLOUD API NVOIN AI AGENT CODE")
    print("=======================================================")
    
    # 1. Uji Gemini API
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"\n[*] Menguji Gemini API (gemini-3.5-flash)...")
        url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
        headers = {"Authorization": f"Bearer {gemini_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gemini-3.5-flash",
            "messages": [{"role": "user", "content": "Sapa pengguna Nvoin AI dalam 1 kalimat bahasa Indonesia singkat."}],
            "temperature": 0.3
        }
        try:
            with httpx.Client(timeout=35.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"].get("content", "")
                    print(f"    [V] SUKSES GEMINI! Respons: \"{content.strip()}\"")
                else:
                    print(f"    [!] Status {res.status_code}: {res.text[:120]}")
        except Exception as e:
            print(f"    [X] Exception Gemini: {str(e)}")
    else:
        print("[!] GEMINI_API_KEY tidak ditemukan di .env")

    # 2. Uji HuggingFace Gemma 4 31B IT
    hf_key = os.getenv("HUGGING_FACE_API_KEY")
    if hf_key:
        print(f"\n[*] Menguji HuggingFace API (google/gemma-4-31B-it)...")
        url = "https://router.huggingface.co/v1/chat/completions"
        headers = {"Authorization": f"Bearer {hf_key}", "Content-Type": "application/json"}
        payload = {
            "model": "google/gemma-4-31B-it",
            "messages": [{"role": "user", "content": "Sapa pengguna Nvoin AI dalam 1 kalimat singkat."}],
            "max_tokens": 100,
            "temperature": 0.3
        }
        try:
            with httpx.Client(timeout=35.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"].get("content", "")
                    print(f"    [V] SUKSES HUGGINGFACE! Respons: \"{content.strip()}\"")
                else:
                    print(f"    [!] Status {res.status_code}: {res.text[:120]}")
        except Exception as e:
            print(f"    [X] Exception HuggingFace: {str(e)}")
    else:
        print("[!] HUGGING_FACE_API_KEY tidak ditemukan di .env")

if __name__ == "__main__":
    test_cloud_models()
