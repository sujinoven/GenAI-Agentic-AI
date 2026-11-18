import json
from datetime import datetime

from src.core.config import GUARD_LOG, TMP_DIR


def log_event(event):
    TMP_DIR.mkdir(exist_ok=True)
    line = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), **event}
    with open(GUARD_LOG, "a", encoding="utf-8") as file:
        file.write(json.dumps(line, ensure_ascii=False) + "\n")


def read_events(user_id=None, limit=100):
    events = []
    if GUARD_LOG.exists():
        events = [json.loads(line) for line in GUARD_LOG.read_text(encoding="utf-8").splitlines() if line.strip()]
    if user_id:
        events = [event for event in events if event.get("user_id") == user_id]
    counts = {"questions" : len(events),
              "blocked"   : sum(event["status"] == "BLOCKED" for event in events),
              "masked_in" : sum(event["masked_in"] for event in events),
              "masked_out": sum(event["masked_out"] for event in events)}
    return {"counts": counts, "events": events[::-1][:limit]}


def clear_events():
    GUARD_LOG.unlink(missing_ok=True)
