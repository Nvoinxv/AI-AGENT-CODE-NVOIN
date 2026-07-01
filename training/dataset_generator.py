import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

SYNTHETIC_TEMPLATES = [
    {
        "user": "Apa perbedaan antara list dan tuple di Python?",
        "manager_decision": {
            "action": "finish",
            "response": "List bersifat mutable (bisa diubah isinya setelah dibuat) dan menggunakan kurung siku `[]`, sedangkan tuple bersifat immutable (tidak bisa diubah) dan menggunakan kurung biasa `()`."
        }
    },
    {
        "user": "Tolong analisis struktur folder di workspace ini dan buatkan rencana refactoring untuk modul autentikasi.",
        "manager_decision": {
            "action": "delegate",
            "agent": "planner",
            "instruction": "Menganalisis direktori workspace dan membuat arsitektur/rencana refactoring untuk modul autentikasi."
        }
    },
    {
        "user": "Buatkan berkas kalkulator.py yang memiliki fungsi tambah, kurang, kali, dan bagi.",
        "manager_decision": {
            "action": "delegate",
            "agent": "coder",
            "instruction": "Menulis berkas kalkulator.py dengan fungsionalitas aritmatika dasar (tambah, kurang, kali, bagi)."
        }
    },
    {
        "user": "Jalankan unit test pada berkas test_kalkulator.py menggunakan pytest dan beritahu jika ada yang error.",
        "manager_decision": {
            "action": "delegate",
            "agent": "executor",
            "instruction": "Menjalankan perintah 'pytest test_kalkulator.py' di terminal dan memeriksa log output/error."
        }
    },
    {
        "user": "Periksa kode di app.py kenapa terjadi MemoryError atau bottleneck saat pemanggilan database.",
        "manager_decision": {
            "action": "delegate",
            "agent": "reviewer",
            "instruction": "Mengaudit app.py untuk menemukan celah kebocoran memori (MemoryError) atau bottleneck query database."
        }
    }
]

def generate_dataset(output_path: str, count: int = 100):
    data: List[Dict[str, Any]] = []
    
    # Perbanyak dataset sintetik dengan variasi
    for idx in range(count):
        template = SYNTHETIC_TEMPLATES[idx % len(SYNTHETIC_TEMPLATES)]
        entry = {
            "id": f"fugu_synth_{idx+1}",
            "instruction": template["user"],
            "manager_output": json.dumps(template["manager_decision"], ensure_ascii=False)
        }
        data.append(entry)

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Berhasil menghasilkan {len(data)} data sintetik Fugu Manager ke '{output_path}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generator Dataset Sintetik Fugu Manager")
    parser.add_argument("--output", type=str, default="data/synthetic_fugu_trajectories.json", help="Path berkas output JSON")
    parser.add_argument("--count", type=int, default=100, help="Jumlah sampel yang dihasilkan")
    args = parser.parse_args()
    
    generate_dataset(args.output, args.count)
