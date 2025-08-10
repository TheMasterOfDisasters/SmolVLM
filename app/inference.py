# inference.py
import torch
import threading
import queue
import logging
from transformers import AutoProcessor, AutoModelForImageTextToText
from PIL import Image
import config

class InferenceWorker:
    def __init__(self, task_queue: queue.Queue, result_queue: queue.Queue,
                 model_path=config.MODEL_ID):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.model_path = model_path

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.bfloat16 if self.device == "cuda" else torch.float32

        logging.info(f"[SmolVLM] Loading model: {self.model_path} on {self.device} ...")
        self.processor = AutoProcessor.from_pretrained(self.model_path)
        self.model = AutoModelForImageTextToText.from_pretrained(
            self.model_path,
            torch_dtype=self.dtype,
            _attn_implementation="sdpa"
            #_attn_implementation="eager",
            #_attn_implementation="flash_attention_2",
        ).to(self.device)
        logging.info(f"[SmolVLM] Model loaded ✅ on {self.device}")

    def analyze_image(self, image_path: str, prompt: str) -> str:
        torch.set_default_device("cuda")
        image = Image.open(image_path).convert("RGB")
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ]
            },
        ]
        logging.info(f"[SmolVLM] Message created ✅ on {self.device}")

        inputs = self.processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self.model.device, dtype=self.dtype)
        logging.info(f"[SmolVLM] Apply chat ✅ on {self.device}")

        generated_ids = self.model.generate(**inputs, do_sample=False, max_new_tokens=128)
        logging.info(f"[SmolVLM] generate ✅ on {self.device}")

        generated_texts = self.processor.batch_decode(generated_ids, skip_special_tokens=True)
        cleaned = generated_texts[0].strip()
        if "Assistant:" in cleaned:
            cleaned = cleaned.split("Assistant:", 1)[1].strip()
        return cleaned

    def start(self):
        # Warmup before starting thread
        logging.info("[InferenceWorker] Running warmup...")
        result_text = self.analyze_image(config.DEMO_IMAGE, "Warmup run")
        logging.info(f"[InferenceWorker] ✅ Warmup complete with result : {result_text}")
        threading.Thread(target=self._worker_loop, daemon=True).start()

    def _worker_loop(self):
        logging.info("[InferenceWorker] Started and waiting for tasks...")
        while True:
            try:
                task = self.task_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                logging.info(f"[InferenceWorker] Processing: {task}")
                result_text = self.analyze_image(task["image_path"], task["prompt"])
                self.result_queue.put({"id": task["id"], "result": result_text})
            except Exception as e:
                self.result_queue.put({"id": task["id"], "error": str(e)})
            finally:
                self.task_queue.task_done()
