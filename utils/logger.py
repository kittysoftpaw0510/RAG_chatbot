import os
from datetime import datetime

LOG_DIR = os.getenv("PERSIST_DIR", ".")
LOG_FILE = os.path.join(LOG_DIR, "server_events.log")


def log_event(user: str, event_type: str, details: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] user={user} event={event_type} details={details}\n") 