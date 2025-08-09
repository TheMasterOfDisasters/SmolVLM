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
        if not prompt:
            yield self.chat_history, gr.update()
            return

        if not image:
            self.task_id_counter += 1
            self.chat_history.append({"role": "user", "content": prompt})
            yield self.chat_history, gr.update(value="")
            self.chat_history.append({"role": "assistant", "content": "❗ Please upload an image first."})
            yield self.chat_history, gr.update()
            return

        self.task_id_counter += 1
        task_id = self.task_id_counter
        self.task_queue.put({"id": task_id, "image_path": image, "prompt": prompt})

        self.chat_history.append({"role": "user", "content": prompt})
        yield self.chat_history, gr.update(value="")

        placeholder_index = len(self.chat_history)
        placeholder_html = '<span class="typing-dots" aria-label="Assistant is typing"><i></i><i></i><i></i></span>'
        self.chat_history.append({"role": "assistant", "content": placeholder_html})
        yield self.chat_history, gr.update()

        while True:
            try:
                result = self.result_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if result["id"] == task_id:
                if "error" in result:
                    self.chat_history[placeholder_index]["content"] = f"❌ Error: {result['error']}"
                else:
                    self.chat_history[placeholder_index]["content"] = result["result"]
                break

        yield self.chat_history, gr.update()

    def start(self):
        with gr.Blocks(
                theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="pink"),
                css="""
                html, body { height: 100%; margin: 0; padding: 0; }
                .gradio-container { 
                    width: 80vw !important; 
                    height: 80vh !important; 
                    min-width: 80vw !important;
                    min-height: 80vh !important;
                    max-width: 80vw !important;
                    max-height: 80vh !important;
                    margin: 0 auto; 
                    display: flex; 
                    flex-direction: column; 
                    justify-content: flex-start;
                }
                /* Remove ALL extra space above header */
                .gradio-container > *:first-child { margin-top: 0 !important; padding-top: 80 !important; }
                body > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }

                /* Chat layout & bubbles */
                #chatbot .message {
                    display: inline-block;
                    flex: 0 1 auto;
                    max-width: min(75%, 1000px);
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
                #chatbot .message > div { max-width: none !important; padding: 0 !important; }
                #chatbot .message p { margin: 0.35em 0; }
                #chatbot .message p:first-child { margin-top: 0; }
                #chatbot .message p:last-child { margin-bottom: 0; }

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

                /* Animated typing indicator */
                .typing-dots { display: inline-flex; gap: 6px; align-items: center; }
                .typing-dots i {
                    width: 6px; height: 6px; border-radius: 50%;
                    background: currentColor; opacity: 0.45;
                    animation: typing-bounce 1.2s infinite ease-in-out;
                    display: inline-block;
                }
                .typing-dots i:nth-child(2) { animation-delay: .15s; }
                .typing-dots i:nth-child(3) { animation-delay: .30s; }
                @keyframes typing-bounce {
                    0%, 80%, 100% { transform: translateY(0); opacity: .35; }
                    40% { transform: translateY(-4px); opacity: .9; }
                }

                #chatbot .avatar, #chatbot .wrap .avatar-container { width: 28px; height: 28px; }
                #chatbot .wrap { gap: 8px; }
                #chatbot .overflow-y-auto { scroll-behavior: smooth; }
                .gradio-container .gr-text-input textarea { border-radius: 14px !important; }
            """
        ) as demo:

            gr.Markdown("<h1 style='color:white; text-align:center; margin:0;'>💬 SmolVLM Chat</h1>")

            with gr.Row():
                chatbot = gr.Chatbot(
                    value=self.chat_history,
                    elem_id="chatbot",
                    height="60vh",
                    scale=1,
                    type="messages",
                    render_markdown=True,
                )
                image_input = gr.Image(
                    type="filepath",
                    label="Uploaded Image",
                    height="60vh",
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
