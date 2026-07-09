import json
import os
import threading
import time
from typing import Optional

from .metrics import get_metrics


_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()


def _worker(path: str, interval: float):
    # append JSON-lines snapshots periodically until stop requested
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    while not _stop_event.wait(interval):
        try:
            snapshot = get_metrics()
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")
        except Exception:
            # never crash the worker
            pass


def start_persistence(path: Optional[str] = None, interval_seconds: Optional[int] = None):
    """Start background thread that appends metrics snapshots to `path` every `interval_seconds`.

    Defaults read from env: `METRICS_PERSIST_PATH` and `PERSIST_INTERVAL_SECONDS` (default 1800s).
    """
    global _thread

    if _thread and _thread.is_alive():
        return

    if path is None:
        path = os.getenv("METRICS_PERSIST_PATH", "metrics_history.jsonl")

    if interval_seconds is None:
        try:
            interval_seconds = int(os.getenv("PERSIST_INTERVAL_SECONDS", "1800"))
        except Exception:
            interval_seconds = 1800

    _stop_event.clear()
    _thread = threading.Thread(target=_worker, args=(path, float(interval_seconds)), daemon=True)
    _thread.start()


def stop_persistence(timeout: float = 2.0):
    """Signal the background worker to stop and wait up to `timeout` seconds."""
    _stop_event.set()
    global _thread
    if _thread:
        _thread.join(timeout=timeout)
        _thread = None
