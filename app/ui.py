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
        if not image or not prompt:
            yield self.chat_history, ""
            return

        self.task_id_counter += 1
        task_id = self.task_id_counter
        self.task_queue.put({"id": task_id, "image_path": image, "prompt": prompt})

        # Append user message immediately
        self.chat_history.append({"role": "user", "content": prompt})
        # Show waiting placeholder for assistant
        self.chat_history.append({"role": "assistant", "content": "⏳ ..."})
        yield self.chat_history, ""  # clear text box

        # Wait for result
        while True:
            try:
                result = self.result_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if result["id"] == task_id:
                # Replace the placeholder with actual content
                self.chat_history[-1] = {"role": "assistant", "content": f"❌ Error: {result['error']}"} if "error" in result else {"role": "assistant", "content": result["result"]}
                break

        yield self.chat_history, ""

    def start(self):
        with gr.Blocks(
                theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="pink"),
                css="""
                #chatbot .message {
                    display: inline-block;
                    flex: 0 1 auto;
                    max-width: min(75%, 800px);
                    min-width: 6ch;
                    padding: 6px 10px;
                    border-radius: 14px;
                    margin: 4px 0;
                    line-height: 1.35;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.08);
                    white-space: pre-wrap;
                    word-break: normal;
                    overflow-wrap: break-word;
                    hyphens: none;
                }
                #chatbot .message .markdown-body,
                #chatbot .message > div { max-width: none !important; }
                #chatbot .message.user {
                    margin-left: auto;
                    background: rgba(42, 157, 143, 0.16);
                    border-top-right-radius: 6px;
                    text-align: right;
                }
                #chatbot .message.assistant {
                    margin-right: auto;
                    background: rgba(38, 70, 83, 0.14);
                    border-top-left-radius: 6px;
                    text-align: left;
                }
                #chatbot .avatar, #chatbot .wrap .avatar-container { width: 28px; height: 28px; }
                #chatbot .wrap { gap: 8px; }
                #chatbot .overflow-y-auto { scroll-behavior: smooth; }
                .gradio-container .gr-text-input textarea { border-radius: 14px !important; }
                """
        ) as demo:

            gr.Markdown("<h1 style='color:white; text-align:center;'>💬 SmolVLM Chat</h1>")

            with gr.Row():
                chatbot = gr.Chatbot(
                    value=self.chat_history,
                    elem_id="chatbot",
                    height=500,
                    scale=1,
                    type="messages",
                    render_markdown=True,
                )
                image_input = gr.Image(
                    type="filepath",
                    label="Uploaded Image",
                    height=500,
                    scale=1
                )

            with gr.Row():
                text_input = gr.Textbox(
                    placeholder="Type your message and press Enter...",
                    show_label=False,
                    lines=1
                )

            text_input.submit(
                fn=self.process_input,
                inputs=[image_input, text_input],
                outputs=[chatbot, text_input]
            )

        demo.queue().launch(server_name="0.0.0.0", server_port=8080)
