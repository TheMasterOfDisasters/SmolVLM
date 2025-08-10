import gradio as gr
import queue
import threading

from result_broker import ResultBroker
import config

class GradioUI:
    def __init__(self, task_queue: queue.Queue, result_broker: ResultBroker):
        self.task_queue = task_queue
        self.result_broker = result_broker
        self.task_id_counter = 0
        self.chat_history = []

    def process_input(self, image, prompt):
        if not prompt:
            yield self.chat_history, gr.update()
            return

        if not image:
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
            # Wait for only our result via the broker
            waiter = self.result_broker.register(task_id)
            try:
                result = waiter.get(timeout=120)
            except queue.Empty:
                self.chat_history[placeholder_index]["content"] = "⌛ Timed out waiting for result."
                break
            if "error" in result:
                self.chat_history[placeholder_index]["content"] = f"❌ Error: {result['error']}"
            else:
                self.chat_history[placeholder_index]["content"] = result["result"]
            break

        yield self.chat_history, gr.update()

    def build(self):
        with gr.Blocks(
                theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="pink", font=[gr.themes.GoogleFont("Roboto"), gr.themes.GoogleFont("Roboto Mono")]),
                css="""
                html, body { height: 100%; margin: 0; padding: 0; }
                .gradio-container { 
                    width: 80vw !important; 
                    min-width: 80vw !important;
                    max-width: 80vw !important;
                    min-height: 100dvh !important;
                    height: auto !important;
                    max-height: none !important;
                    margin: 0 auto; 
                    display: flex; 
                    flex-direction: column; 
                    justify-content: flex-start;
                }
                /* Remove all extra space above header */
                .gradio-container > *:first-child { margin-top: 0 !important; padding-top: 0 !important; }
                body > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }

                /* Chat layout & bubbles */
                #chatbot .message {
                    display: inline-block;
                    flex: 0 1 auto;
                    max-width: min(75%, 1000px);
                    min-width: 30ch;
                    padding: 2px 4px;
                    border-radius: 14px;
                    margin: 4px 0;
                    line-height: 0.35;
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

                /* Layout fixes: let the middle row flex and shrink */
                #main-row {
                    flex: 1 1 auto;
                    min-height: 0;
                    display: flex;
                }
                #main-row > * {
                    height: 100% !important;
                    min-height: 0;
                }
                #chatbot,
                #chatbot .overflow-y-auto {
                    height: 100% !important;
                    min-height: 0 !important;
                }
            """
        ) as demo:

            gr.Markdown(f"<h1 style='color:white; text-align:center; margin:0;'>💬 SmolVLM Chat</h1>\n<p style='text-align:center; margin-top:6px;'>Model: <code>{config.MODEL_ID}</code></p>")

            with gr.Row(elem_id="main-row"):
                chatbot = gr.Chatbot(
                    value=self.chat_history,
                    elem_id="chatbot",
                    scale=1,
                    type="messages",
                    render_markdown=True,
                )
                image_input = gr.Image(
                    type="filepath",
                    label="Uploaded Image",
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

        return demo
