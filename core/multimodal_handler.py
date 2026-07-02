import os
import base64
from pathlib import Path
from typing import List, Dict, Any, Tuple
from tools.file_tools import ReadFileTool
from tools.search_tools import ListDirectoryTool
from tools.web_tools import FetchWebPageTool

class MultimodalHandler:
    """
    Pra-pemroses pintar untuk Nvoin AI.
    Menyelesaikan mentions (@file, @folder), memuat gambar (base64) untuk Gemini & Gemma Vision,
    dan mengeksekusi fetch browser sebelum prompt dikirim ke Manajer/Sub-Agen.
    """
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.read_tool = ReadFileTool(workspace_dir, allow_outside_workspace=True)
        self.list_tool = ListDirectoryTool(workspace_dir, allow_outside_workspace=True)
        self.browser_tool = FetchWebPageTool()

    def process_input(self, prompt: str, attachments: List[Dict[str, Any]] = None) -> Tuple[str, List[str]]:
        """
        Mengembalikan tuple: (processed_prompt_string, list_of_base64_image_strings)
        """
        enriched_prompt = prompt
        images_list: List[str] = []

        # 1. Analisis lampiran eksplisit dari Frontend GUI
        if attachments:
            for att in attachments:
                att_type = att.get("type", "").lower()
                content = att.get("content", "").strip()

                if att_type == "image":
                    img_b64 = self._encode_image_to_base64(content)
                    if img_b64:
                        images_list.append(img_b64)
                        enriched_prompt += f"\n[Lampiran Gambar Vision Dimuat: {content}]"
                    else:
                        enriched_prompt += f"\n[Catatan Vision: Lampiran gambar '{content}' dilampirkan]"

                elif att_type == "mention":
                    enriched_prompt += self._resolve_mention(content)

                elif att_type == "browser":
                    url = content.replace("Fetch documentation from ", "").strip()
                    if "http" in url:
                        web_res = self.browser_tool.execute(url)
                        enriched_prompt += f"\n[Hasil Web Browser]\n{web_res}\n"
                    else:
                        enriched_prompt += f"\n[Instruksi Web Browser]: {content}\n"

                elif att_type == "action":
                    enriched_prompt += f"\n[Instruksi Aksi Terminal CLI]: {content}\n"

        # 2. Deteksi inline mention dalam teks prompt (misal: @C:\path\to\file.py)
        words = prompt.split()
        for w in words:
            if w.startswith("@") and len(w) > 2:
                mention_path = w[1:]
                # Hindari mention kata kunci umum (@planner, @coder, dll)
                if mention_path.lower() not in ["planner", "coder", "executor", "reviewer", "nvoin"]:
                    enriched_prompt += self._resolve_mention(mention_path)

        return enriched_prompt, images_list

    def _resolve_mention(self, mention_str: str) -> str:
        clean_path = mention_str.strip().lstrip("@")
        p = Path(clean_path)
        
        # Cek apakah absolut atau relatif terhadap workspace
        target = p if p.is_absolute() else (self.workspace_dir / p)

        if target.exists():
            if target.is_dir():
                res = self.list_tool.execute(str(target))
                return f"\n=== [Resolusi Mention Folder: {clean_path}] ===\n{res}\n"
            elif target.is_file():
                res = self.read_tool.execute(str(target))
                return f"\n=== [Resolusi Mention File: {clean_path}] ===\n{res[:4000]}\n"
        
        return f"\n[Mention Agent/Konteks: {clean_path}]\n"

    def _encode_image_to_base64(self, img_reference: str) -> str:
        """Mengonversi path file gambar atau header base64 menjadi string base64 bersih."""
        if "base64," in img_reference:
            return img_reference.split("base64,")[-1]
        
        # Bersihkan deskripsi kurung siku jika dikirim dari frontend mock
        clean_ref = img_reference.replace("[Image Attachment:", "").replace("]", "").strip()
        p = Path(clean_ref)
        target = p if p.is_absolute() else (self.workspace_dir / p)

        if target.exists() and target.is_file():
            try:
                with open(target, "rb") as f:
                    return base64.b64encode(f.read()).decode("utf-8")
            except Exception:
                pass
        return None
