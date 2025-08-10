# SmolVLM — Easy-to-Run Vision-Language Model 🖼️💬

This [project](https://github.com/TheMasterOfDisasters/SmolVLM) packages [SmolVLM2](https://huggingface.co/HuggingFaceTB/SmolVLM2-500M-Video-Instruct) into a **ready-to-use Docker image** with both a **web UI** and an **HTTP API** for image–text-to-text tasks.

It’s designed for **fast setup** and **offline-friendly deployment** so you can:
- Pull the container
- Run it with one command
- Start sending images and prompts instantly

⚠️ **Note:** Maintained by an independent developer for ease-of-use.  
Not production-hardened — you may need extra work for critical deployments.

✅ **Offline Mode:** Supported — models can be pre-baked into the image or mounted from local storage.  
✅ **Minimal GPU Requirements:** Works on most modern NVIDIA GPUs with **at least 4GB VRAM** and CUDA support (Ampere or newer recommended). Lower VRAM cards may require using the 256M model variant.

🤝 **Contributions Welcome:** Bug fixes, feature requests, and PRs are appreciated.

---

## 🆘 Support & Issues
If you encounter problems or have suggestions:
- Open a [GitHub Issue](https://github.com/TheMasterOfDisasters/SmolVLM/issues) with details, logs, and reproduction steps
- Use [Discussions](https://github.com/TheMasterOfDisasters/SmolVLM/discussions) for general questions

---

## 🚀 Quick Start

```bash
docker run --gpus all -p 8888:8888 sensejworld/smolvlm:latest
```

Then open: **[http://localhost:8888/ui](http://localhost:8888/ui)**

---

## 🌐 API Usage Example

```bash
curl -X POST "http://localhost:8888/ptt/convert" \
  -H "Accept: application/json" \
  -F "query=What is in this image?" \
  -F "image=@cat.jpg;type=image/jpeg"
```

Or without an image (uses demo image):

```bash
curl -X POST "http://localhost:8888/ptt/convert" \
  -F "query=Count cats in the image?"
```

---

## 📦 Docker Features
- Pinned dependencies for reproducibility
- GPU acceleration (CUDA)
- Preloaded model option for full offline usage
- Single container with UI + API
- Clean multi-stage build

---

## 🐳 Docker Hub
Find available images on [Docker Hub](https://hub.docker.com/r/sensejworld/smolvlm/tags) — useful for:
- Selecting a specific version
- Checking the latest builds before pulling
- Matching CUDA/PyTorch versions to your needs

---

## 📜 Version History

### v0.0.2 (Planned)
- Support picture Batch
- Support video

### v0.0.1
- Initial release
- Basic SmolVLM2 inference via API & UI
- Demo image support
- Docker GPU support
- Added FastAPI-based `/ptt/convert` endpoint
- Integrated Gradio chat UI with image upload
- Shared inference worker between API and UI
- Offline model prefetch script (`init_downloads.py`)
  Run with:
```bash
docker run --gpus all -p 8888:8888 sensejworld/smolvlm:v0.0.1
```

---

## 🛠 Developer Notes
See [`notes.md`](https://github.com/TheMasterOfDisasters/SmolVLM/blob/main/docs/notes.md) for:
- Local Docker build/run instructions
- Conda setup for local dev
- FlashAttention verification commands
- API & UI testing commands

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).  
Models by [HuggingFaceTB](https://huggingface.co/HuggingFaceTB) — check their respective licenses.
