"""
Skrip pelatihan QLoRA (Supervised Fine-Tuning) untuk model open source
sekelas Gemma 4 12B agar dapat bertindak sebagai Fugu Manager.
Menggunakan library Unsloth dan TRL SFTTrainer.
"""
import os
import argparse

def train_fugu_manager(dataset_path: str, model_name: str, output_dir: str):
    print(f"=== MEMULAI PELATIHAN FUGU MANAGER ({model_name}) ===")
    print(f"Dataset : {dataset_path}")
    print(f"Output  : {output_dir}")

    try:
        from unsloth import FastLanguageModel
        import torch
        from datasets import load_dataset
        from trl import SFTTrainer
        from transformers import TrainingArguments
    except ImportError:
        print("\nPeringatan: Dependensi training (unsloth, torch, trl, transformers) belum diinstal.")
        print("Silakan jalankan: pip install unsloth trl transformers datasets torch")
        return

    max_seq_length = 2048
    dtype = None  # Auto detection (Float16 / Bfloat16)
    load_in_4bit = True  # QLoRA 4-bit quantization untuk efisiensi VRAM model 12B

    print("\n[1/4] Memuat model dan tokenizer...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        dtype=dtype,
        load_in_4bit=load_in_4bit
    )

    print("[2/4] Menambahkan konfigurasi LoRA Adapter...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=16,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing="unsloth"
    )

    print("[3/4] Memuat dataset SFT JSONL...")
    dataset = load_dataset("json", data_files=dataset_path, split="train")

    print("[4/4] Konfigurasi SFTTrainer...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="conversations",
        max_seq_length=max_seq_length,
        dataset_num_proc=2,
        packing=False,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=60,
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=1,
            output_dir=output_dir,
            optim="adamw_8bit"
        ),
    )

    print("\nMenjalankan proses fine-tuning...")
    trainer_stats = trainer.train()
    print(f"\nPelatihan selesai! Statistik: {trainer_stats}")

    print(f"Menyimpan adapter ke '{output_dir}'...")
    model.save_pretrained_merged(output_dir, tokenizer, save_method="merged_16bit")
    print("Berhasil menyimpan model!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QLoRA Fine-Tuning untuk Gemma 12B Fugu Manager")
    parser.add_argument("--dataset", type=str, required=True, help="Path ke berkas dataset SFT JSONL")
    parser.add_argument("--model_name", type=str, default="unsloth/gemma-2-9b-bnb-4bit", help="HuggingFace model ID (representasi model kelas 12B)")
    parser.add_argument("--output_dir", type=str, default="outputs/fugu_gemma_manager", help="Folder output adapter model")
    args = parser.parse_args()

    train_fugu_manager(args.dataset, args.model_name, args.output_dir)
