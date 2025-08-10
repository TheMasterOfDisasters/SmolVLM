# init_downloads.py
"""
Pre-download all supported SmolVLM models to Hugging Face caches,
so the image runs fully offline at runtime.
"""
import os
from huggingface_hub import snapshot_download

MODELS = [
    "HuggingFaceTB/SmolVLM2-256M-Video-Instruct",
    "HuggingFaceTB/SmolVLM2-500M-Video-Instruct",
    #"HuggingFaceTB/SmolVLM2-2.2B-Base",
    #"HuggingFaceTB/SmolVLM2-2.2B-Instruct",
]

IGNORE_PATTERNS = [
    "*.md", "*.onnx", "*.h5", "*.tflite",
    "rust_model*", "*.msgpack", "tf_model*"
]

def main():
    # Use env-defined caches (HF_HOME/TRANSFORMERS_CACHE/HUGGINGFACE_HUB_CACHE)
    for repo_id in MODELS:
        print(f"[prefetch] {repo_id}")
        snapshot_download(repo_id=repo_id, local_files_only=False, ignore_patterns=IGNORE_PATTERNS)

if __name__ == "__main__":
    main()
