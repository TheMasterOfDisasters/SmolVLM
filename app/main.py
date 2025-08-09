import queue, time, logging
from inference import InferenceWorker

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    task_queue = queue.Queue()
    result_queue = queue.Queue()

    worker = InferenceWorker(task_queue, result_queue)
    worker.start()
