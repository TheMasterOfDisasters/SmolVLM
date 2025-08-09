import logging
import threading
import time
import tempfile
import shutil
from nicegui import ui

class SmolVLM_UI:
    def __init__(self, task_queue, result_queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self._stop_event = threading.Event()

        # Store uploaded image path
        self.uploaded_file_path = {"path": None}

        # UI elements
        self.chat_container = ui.column().style('max-height: 500px; overflow-y: auto;')
        self.prompt_input = ui.input("Enter prompt", value="Describe image")
        ui.upload(on_upload=self.handle_upload, label="Upload Image")
        ui.button("Run Inference", on_click=self.send_task)

    def handle_upload(self, e):
        """Save uploaded file to temp dir and store path."""
        temp_dir = tempfile.gettempdir()
        file_path = f"{temp_dir}/{e.name}"
        with open(file_path, "wb") as f:
            shutil.copyfileobj(e.content, f)
        self.uploaded_file_path["path"] = file_path
        logging.info(f"[UI] Uploaded: {file_path}")
        ui.notify(f"Uploaded: {e.name}")

    def send_task(self):
        """Send a task to the inference worker."""
        if not self.uploaded_file_path["path"]:
            ui.notify("❌ No image uploaded", color="negative")
            return
        task = {
            "id": time.time(),
            "image_path": self.uploaded_file_path["path"],
            "prompt": self.prompt_input.value
        }
        self.task_queue.put(task)
        self.add_chat_message("🧑‍💻 You", self.prompt_input.value)
        self.add_chat_message("🤖 Assistant", "⏳ Processing...")

    def add_chat_message(self, sender, message):
        """Append message to chat container."""
        with self.chat_container:
            ui.markdown(f"**{sender}:** {message}")

    def _result_listener(self):
        """Background listener for inference results."""
        while not self._stop_event.is_set():
            try:
                result = self.result_queue.get(timeout=0.1)
            except:
                continue

            # Remove last "Processing..." and replace with actual result
            if "error" in result:
                self.add_chat_message("🤖 Assistant", f"❌ {result['error']}")
            else:
                self.add_chat_message("🤖 Assistant", result["result"])
            self.result_queue.task_done()

    def start(self):
        logging.info("[UI] Starting NiceGUI server...")
        threading.Thread(target=self._result_listener, daemon=True).start()
        ui.run(reload=False)

    def stop(self):
        self._stop_event.set()
