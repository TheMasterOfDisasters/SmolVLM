import torch
torch.set_default_device("cuda")  # 🔥 Forces all tensors to default to GPU

from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image

# Config
MODEL_PATH = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE = torch.bfloat16 if DEVICE == "cuda" else torch.float32
LOCAL_IMAGE = "images/cat.jpg"
PROMPT = "Can you describe this image?"

print(f"[SmolVLM] Loading model: {MODEL_PATH} on {DEVICE} ...")
processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_PATH,
    torch_dtype=DTYPE,
    _attn_implementation="eager",
).to(DEVICE)
print(f"[SmolVLM] Model loaded ✅ on {DEVICE}")

def analyze_image(image_path: str, prompt: str):
    # Load local image
    image = Image.open(image_path).convert("RGB")

    # Create chat message
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
            ]
        },
    ]
    print(f"[SmolVLM] Message created ✅ on {DEVICE}")

    # Preprocess
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device, dtype=DTYPE)
    print(f"[SmolVLM] Apply chat ✅ on {DEVICE}")

    # Generate
    generated_ids = model.generate(**inputs, do_sample=False, max_new_tokens=128)
    print(f"[SmolVLM] generate ✅ on {DEVICE}")

    # Decode
    generated_texts = processor.batch_decode(generated_ids, skip_special_tokens=True)
    return generated_texts[0]

if __name__ == "__main__":
    result = analyze_image(LOCAL_IMAGE, PROMPT)
    print("\n[Result]:", result)
