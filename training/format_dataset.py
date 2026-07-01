import json
import argparse
from pathlib import Path
from models.prompts import FUGU_MANAGER_PROMPT

def convert_to_sharegpt(input_path: str, output_path: str):
    in_file = Path(input_path)
    if not in_file.exists():
        print(f"Error: Berkas input '{input_path}' tidak ditemukan.")
        return

    with open(in_file, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    formatted_lines = []
    for item in raw_data:
        user_msg = item["instruction"]
        assistant_msg = item["manager_output"]
        
        system_context = FUGU_MANAGER_PROMPT.format(
            subagent_summary="Belum ada delegasi tugas ke sub-agen.",
            user_prompt=user_msg
        )

        sharegpt_entry = {
            "conversations": [
                {"from": "system", "value": system_context},
                {"from": "human", "value": user_msg},
                {"from": "gpt", "value": assistant_msg}
            ]
        }
        formatted_lines.append(json.dumps(sharegpt_entry, ensure_ascii=False))

    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(formatted_lines))

    print(f"Berhasil mengonversi {len(formatted_lines)} sampel ke format ShareGPT JSONL: '{output_path}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Konverter Format Dataset SFT / ShareGPT")
    parser.add_argument("--input", type=str, required=True, help="Path berkas input JSON sintetik")
    parser.add_argument("--output", type=str, default="data/gemma_sft.jsonl", help="Path berkas output JSONL")
    args = parser.parse_args()

    convert_to_sharegpt(args.input, args.output)
