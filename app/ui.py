import gradio as gr
import queue
import threading

class GradioUI:
    def __init__(self, task_queue: queue.Queue, result_queue: queue.Queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.task_id_counter = 0
        self.chat_history = []

    def process_input(self, image, prompt):
        """Send task to inference worker and wait for result."""
        if not image or not prompt:
            return self.chat_history

        self.task_id_counter += 1
        task_id = self.task_id_counter
        self.task_queue.put({"id": task_id, "image_path": image, "prompt": prompt})

        # Wait for result (simple blocking wait, can be async later)
        while True:
            try:
                result = self.result_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if result["id"] == task_id:
                if "error" in result:
                    self.chat_history.append(("You", prompt))
                    self.chat_history.append(("Assistant", f"❌ Error: {result['error']}"))
                else:
                    self.chat_history.append(("You", prompt))
                    self.chat_history.append(("Assistant", result["result"]))
                break

        return self.chat_history

    def start(self):
        with gr.Blocks(theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="pink"), css=".gradio-container {background-color: #0d1117 !important;}") as demo:
            gr.Markdown("<h1 style='color:white; text-align:center;'>💬 SmolVLM Chat</h1>")

            chatbot = gr.Chatbot(value=self.chat_history, elem_id="chatbot", height=500)
            with gr.Row():
                image_input = gr.Image(type="filepath", label="Upload an image", height=200)
                text_input = gr.Textbox(label="Prompt", placeholder="Ask me anything about the image...")

            submit_btn = gr.Button("Send", variant="primary")

            submit_btn.click(
                fn=self.process_input,
                inputs=[image_input, text_input],
                outputs=[chatbot]
            )

        demo.queue().launch(server_name="0.0.0.0", server_port=8080)

