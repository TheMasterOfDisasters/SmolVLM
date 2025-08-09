import torch
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image

torch.set_default_device("cuda")
# Model path
MODEL_PATH = "HuggingFaceTB/SmolVLM2-500M-Video-Instruct"

processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = AutoModelForImageTextToText.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.bfloat16,
    _attn_implementation="eager"
).to("cuda")
print(f"[SmolVLM] Model loaded ✅ on cuda")

def analyze_image(image_path: str):
    # Load image
    image = Image.open(image_path).convert("RGB")

    # Create chat-style message
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/bee.jpg"},
                {"type": "text", "text": "Can you describe this image?"},
            ]
        },
    ]

    print(f"[SmolVLM] Message created ✅ on cuda")
    # Apply chat template
    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        tokenize=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device, dtype=torch.bfloat16)
    print(f"[SmolVLM] Apply chat ✅ on cuda")

    generated_ids = model.generate(**inputs, do_sample=False, max_new_tokens=64)
    print(f"[SmolVLM] generate ✅ on cuda")

    generated_texts = processor.batch_decode(
        generated_ids,
        skip_special_tokens=True,
    )

    print(f"[SmolVLM] generate ✅ on cuda")
    print(generated_texts[0])

if __name__ == "__main__":
    test_image = "images/cat.jpg"
    analyze_image(test_image)
