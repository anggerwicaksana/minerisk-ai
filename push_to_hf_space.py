"""One-Click Deployment Script for Hugging Face Spaces.
Uploads MineRisk-AI code, calibrated model artifacts, and sample data
to https://huggingface.co/spaces/anggerw/minerisk-ai.
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, login

BASE_DIR = Path(__file__).resolve().parent
REPO_ID = "anggerw/minerisk-ai"


def deploy_to_spaces():
    print(f"🚀 Deploying MineRisk-AI to Hugging Face Spaces: {REPO_ID}...")
    api = HfApi()

    # Upload root deployment files
    root_files = ["app.py", "mcp_server.py", "requirements.txt", "README.md"]
    for f in root_files:
        path = BASE_DIR / f
        if path.exists():
            print(f"  Uploading {f}...")
            api.upload_file(
                path_or_fileobj=str(path),
                path_in_repo=f,
                repo_id=REPO_ID,
                repo_type="space",
            )

    # Upload src folder
    src_dir = BASE_DIR / "src"
    if src_dir.exists():
        print("  Uploading src/ module...")
        api.upload_folder(
            folder_path=str(src_dir),
            path_in_repo="src",
            repo_id=REPO_ID,
            repo_type="space",
        )

    # Upload artifacts folder (lightweight model, metrics, and demo sample)
    art_dir = BASE_DIR / "artifacts"
    if art_dir.exists():
        print("  Uploading artifacts/ (calibrated model, metadata, sample panel)...")
        api.upload_folder(
            folder_path=str(art_dir),
            path_in_repo="artifacts",
            repo_id=REPO_ID,
            repo_type="space",
            ignore_patterns=["*.tmp", "*checkpoint*"],
        )

    print("\n✅ Successfully deployed to Hugging Face Spaces!")
    print(f"🌐 Live Web Demo: https://huggingface.co/spaces/{REPO_ID}")
    print(f"🔌 MCP Endpoint:  https://{REPO_ID.replace('/', '-')}.hf.space/gradio_api/mcp")


if __name__ == "__main__":
    deploy_to_spaces()
