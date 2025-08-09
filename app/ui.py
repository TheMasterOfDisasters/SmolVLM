import gradio as gr
import queue
import threading

class GradioUI:
    def __init__(self, task_queue: queue.Queue, result_queue: queue.Queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.task_id_counter = 0
        # Keep history as a list; we'll store role-based messages so CSS can target them
        self.chat_history = []

    def process_input(self, image, prompt):
        """Send task to inference worker and wait for result."""
        if not image or not prompt:
            return self.chat_history

        self.task_id_counter += 1
        task_id = self.task_id_counter
        self.task_queue.put({"id": task_id, "image_path": image, "prompt": prompt})

        # Immediately add the user message so it's visible while we wait
        self.chat_history.append({"role": "user", "content": prompt})

        # Wait for result (simple blocking wait, can be async later)
        while True:
            try:
                result = self.result_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            if result["id"] == task_id:
                if "error" in result:
                    self.chat_history.append({"role": "assistant", "content": f"❌ Error: {result['error']}"})
                else:
                    self.chat_history.append({"role": "assistant", "content": result["result"]})
                break

        return self.chat_history

    def start(self):
        with gr.Blocks(
                theme=gr.themes.Soft(primary_hue="cyan", secondary_hue="pink"),
                css="""
                /* ===== Chat layout & bubbles ===== */
                #chatbot .message {
                    display: inline-block;           /* size to content, not full row */
                    flex: 0 1 auto;                  /* prevent over-squeezing */
                    max-width: min(80%, 900px);      /* sensible max width */
                    min-width: 6ch;                  /* avoid vertical text like c
a
t */
                    padding: 10px 12px;
                    border-radius: 16px;             /* rounded corners */
                    margin: 6px 0;
                    line-height: 1.45;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.08);

                    /* Text wrapping rules */
                    white-space: pre-wrap;           /* keep newlines */
                    word-break: normal;              /* don't break words into letters */
                    overflow-wrap: anywhere;         /* break long URLs/long words when needed */
                    hyphens: auto;
                }

                /* Remove inner width clamps some themes add to markdown */
                #chatbot .message .markdown-body,
                #chatbot .message > div { max-width: none !important; }

                /* Right-align user messages */
                #chatbot .message.user {
                    margin-left: auto;               /* push to the right */
                    background: rgba(42, 157, 143, 0.16); /* subtle teal */
                    border-top-right-radius: 6px;    /* asymmetry for bubble feel */
                    text-align: right;
                }

                /* Left-align assistant messages */
                #chatbot .message.assistant {
                    margin-right: auto;              /* push to the left */
                    background: rgba(38, 70, 83, 0.14);  /* subtle slate */
                    border-top-left-radius: 6px;
                    text-align: left;
                }

                /* Reduce avatar footprint if present */
                #chatbot .avatar, #chatbot .wrap .avatar-container { width: 28px; height: 28px; }

                /* Tidy up the Chatbot container */
                #chatbot .wrap { gap: 8px; }

                /* Scroll area polish */
                #chatbot .overflow-y-auto { scroll-behavior: smooth; }

                /* Input box styling */
                .gradio-container .gr-text-input textarea { border-radius: 14px !important; }
                """
        ) as demo:

            gr.Markdown("<h1 style='color:white; text-align:center;'>💬 SmolVLM Chat</h1>")

            # Top row: Chat on left, Image on right
            with gr.Row():
                chatbot = gr.Chatbot(
                    value=self.chat_history,
                    elem_id="chatbot",
                    height=500,
                    scale=1,
                    type="messages",            # enables role-based styling (user/assistant)
                    render_markdown=True,
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
