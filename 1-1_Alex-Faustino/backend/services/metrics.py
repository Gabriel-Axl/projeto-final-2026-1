import threading
import time
from typing import Dict, Any
from datetime import datetime, timezone


_lock = threading.Lock()

# record process start time for uptime
_start_time = time.time()

# counters for simple counts
_counters: Dict[str, int] = {
    "llm_calls": 0,
    "llm_fallbacks": 0,
    "predictions": 0,
}

# cost tracking (estimated)
_total_cost = 0.0

# latency stats per endpoint: store count and total_time to compute average
_latency_stats: Dict[str, Dict[str, float]] = {}


def increment_counter(name: str, n: int = 1) -> None:
    with _lock:
        _counters[name] = _counters.get(name, 0) + n


def add_cost(amount: float) -> None:
    global _total_cost
    with _lock:
        _total_cost += float(amount)


def record_latency(endpoint: str, duration_sec: float) -> None:
    with _lock:
        s = _latency_stats.get(endpoint)
        if s is None:
            s = {"count": 0.0, "total_sec": 0.0}
            _latency_stats[endpoint] = s
        s["count"] += 1
        s["total_sec"] += float(duration_sec)


def _format_uptime(seconds: float) -> str:
    # human-readable uptime
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


def get_metrics() -> Dict[str, Any]:
    with _lock:
        latency = {
            endpoint: {
                "count": int(vals["count"]),
                "avg_sec": (vals["total_sec"] / vals["count"]) if vals["count"] > 0 else 0.0,
                "total_sec": vals["total_sec"],
            }
            for endpoint, vals in _latency_stats.items()
        }

        now = time.time()
        uptime_seconds = now - _start_time
        iso_timestamp = datetime.fromtimestamp(now, tz=timezone.utc).astimezone().isoformat()

        return {
            "counters": dict(_counters),
            "estimated_total_cost": round(_total_cost, 6),
            "latency": latency,
            "timestamp": iso_timestamp,
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime": _format_uptime(uptime_seconds),
        }
