"""Uploads the static showcase files to Hugging Face Space anggerw/minerisk-ai."""

import os
from pathlib import Path
from huggingface_hub import HfApi

REPO_ID = "anggerw/minerisk-ai"
STATIC_DIR = Path(__file__).resolve().parent.parent / "hf_space_static"

def deploy():
    print(f"Mengunggah file statis ke Hugging Face Space: {REPO_ID}...")
    token = os.environ.get("HF_TOKEN")
    api = HfApi(token=token) if token else HfApi()
    
    api.upload_folder(
        folder_path=str(STATIC_DIR),
        repo_id=REPO_ID,
        repo_type="space",
        commit_message="Perbarui tautan notebook Colab dan dokumen panduan",
    )
    print("Berhasil memperbarui Hugging Face Space.")

if __name__ == "__main__":
    deploy()
