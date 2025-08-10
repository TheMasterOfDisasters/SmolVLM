import threading
import queue
import logging

class ResultBroker:
    """
    A small router that decouples producers (inference worker)
    from multiple consumers (UI, API requests). Each task_id gets its own
    one-shot queue. Results can arrive before or after a consumer registers.
    """
    def __init__(self):
        self.incoming = queue.Queue()
        self._waiters = {}          # task_id -> Queue
        self._pending = {}          # task_id -> result dict (arrived early)
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logging.info("[ResultBroker] Started ✅")

    def register(self, task_id: int) -> queue.Queue:
        """
        Register interest in a given task_id and return a Queue that will
        receive exactly one result dict for that id.
        If the result already arrived, returns a queue pre-filled with it.
        """
        q = queue.Queue(maxsize=1)
        with self._lock:
            if task_id in self._pending:
                q.put(self._pending.pop(task_id))
            else:
                self._waiters[task_id] = q
        return q

    def _loop(self):
        while True:
            result = self.incoming.get()
            task_id = result.get("id")
            if task_id is None:
                continue
            with self._lock:
                q = self._waiters.pop(task_id, None)
                if q is not None:
                    q.put(result)
                else:
                    # No one is waiting yet; stash it
                    self._pending[task_id] = result
            self.incoming.task_done()
