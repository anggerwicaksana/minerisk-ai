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
    print(f"🚀 Deploying MineRisk-AI Static Web Showcase to Hugging Face Spaces: {REPO_ID}...")
    api = HfApi()

    static_dir = BASE_DIR / "hf_space_static"
    if static_dir.exists():
        print(f"  Uploading folder {static_dir} -> Space {REPO_ID}...")
        api.upload_folder(
            folder_path=str(static_dir),
            repo_id=REPO_ID,
            repo_type="space",
            commit_message="feat: update title, canonical address, and bold amber favicon",
        )

    print("\n✅ Successfully deployed to Hugging Face Spaces!")
    print(f"🌐 Space URL:        https://huggingface.co/spaces/{REPO_ID}")
    print(f"🌐 Direct Static:   https://{REPO_ID.replace('/', '-')}.static.hf.space/index.html")


if __name__ == "__main__":
    deploy_to_spaces()

