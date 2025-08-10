import os
import uuid
import queue
import logging
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
import config

class ApiHandler:
    """
    Provides a FastAPI app mounted at /ptt for API calls.
    API uses the shared task_queue and a ResultBroker to await results
    without interfering with the Gradio UI.
    """
    def __init__(self, task_queue: queue.Queue, result_broker, storage_dir: str = "uploads"):
        self.task_queue = task_queue
        self.result_broker = result_broker
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

        app = FastAPI(title="PTT API", version="1.0.0")
        self.app = app

        @app.post("/convert")
        async def convert(image: UploadFile = File(None), query: str = Form(...)):
            if not query:
                raise HTTPException(status_code=400, detail="Query is required.")

            # Branch: no image provided -> use demo file directly
            if image is None:
                fpath = config.DEMO_IMAGE
                if not os.path.exists(fpath):
                    raise HTTPException(status_code=500, detail=f"Demo image not found at {fpath}")
            else:
                # Persist the uploaded image to disk (worker expects a path)
                suffix = os.path.splitext(image.filename or "")[1] or ".png"
                fname = f"{uuid.uuid4().hex}{suffix}"
                fpath = os.path.join(self.storage_dir, fname)
                try:
                    data = await image.read()
                    with open(fpath, "wb") as f:
                        f.write(data)
                except Exception as e:
                    logging.exception("Failed to store uploaded file")
                    raise HTTPException(status_code=500, detail=f"Failed to store file: {e}")

            # Enqueue task and wait for result via ResultBroker
            task_id = uuid.uuid4().int & ((1<<31)-1)  # fits in 32-bit signed
            self.task_queue.put({"id": task_id, "image_path": fpath, "prompt": query})

            waiter = self.result_broker.register(task_id)

            # Wait for result in a thread so we don't block the event loop
            def wait_for_result(timeout=120):
                try:
                    return waiter.get(timeout=timeout)
                except queue.Empty:
                    raise TimeoutError("Timed out waiting for inference result")

            try:
                result = await run_in_threadpool(wait_for_result)
            except TimeoutError as e:
                raise HTTPException(status_code=504, detail=str(e))

            if "error" in result:
                return JSONResponse(status_code=500, content={"id": task_id, "error": result["error"]})

            return {"id": task_id, "result": result.get("result", "")}
