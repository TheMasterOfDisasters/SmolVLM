import logging, queue
import uvicorn
import config
from ui import GradioUI
from inference import InferenceWorker
from api_handler import ApiHandler
from result_broker import ResultBroker
from gradio.routes import mount_gradio_app
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.responses import RedirectResponse

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Shared task queue -> consumed by InferenceWorker
    task_queue = queue.Queue()

    # ResultBroker sits between the worker and any consumers (UI/API)
    broker = ResultBroker()

    # Start the single inference worker (GPU/CPU bound)
    worker = InferenceWorker(task_queue, broker.incoming, model_path=config.MODEL_ID)
    worker.start()

    # Build Gradio UI (do not launch server)
    ui_app = GradioUI(task_queue, broker)
    demo = ui_app.build().queue()

    # FastAPI root app

app = FastAPI(title="App + UI + API")

@app.get("/")
async def root_redirect():
    return RedirectResponse(url="/ui")

@app.get("/health", response_class=PlainTextResponse)
async def health():
    return "ok"

# Mount Gradio at root ("/")
mount_gradio_app(app, demo, path="/ui")

# Mount API under /ptt
api = ApiHandler(task_queue, broker)
app.mount("/ptt", api.app)

# Run a single server for both UI and API on the same port
uvicorn.run(app, host="0.0.0.0", port=config.PORT)
