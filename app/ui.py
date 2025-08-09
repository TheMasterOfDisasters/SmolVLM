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
        with gr.Blocks(
                theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="pink"),
                css="""
                .gr-chatbot .wrap.svelte-1jphygv.user {
                    justify-content: flex-end !important;
                    text-align: right !important;
                }
                .gr-chatbot .wrap.svelte-1jphygv.assistant {
                    justify-content: flex-start !important;
                    text-align: left !important;
                }
                """
        ) as demo:

            gr.Markdown("<h1 style='color:white; text-align:center;'>💬 SmolVLM Chat</h1>")

            # Top row: Chat on left, Image on right
            with gr.Row():
                chatbot = gr.Chatbot(
                    value=self.chat_history,
                    elem_id="chatbot",
                    height=500,
                    scale=1
                )
                image_input = gr.Image(
                    type="filepath",
                    label="Uploaded Image",
                    height=500,
                    scale=1
                )

            # Bottom row: Text input full width
            with gr.Row():
                text_input = gr.Textbox(
                    placeholder="Type your message and press Enter...",
                    show_label=False,
                    lines=1
                )

            # Bind Enter to send
            text_input.submit(
                fn=self.process_input,
                inputs=[image_input, text_input],
                outputs=[chatbot]
            )

        demo.queue().launch(server_name="0.0.0.0", server_port=8080)

