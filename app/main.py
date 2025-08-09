import queue, logging
from ui import GradioUI
from inference import InferenceWorker

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    task_queue = queue.Queue()
    result_queue = queue.Queue()

    worker = InferenceWorker(task_queue, result_queue)
    worker.start()

    # Start UI (blocks here until shutdown)
    ui_app = GradioUI(task_queue, result_queue)
    ui_app.start()