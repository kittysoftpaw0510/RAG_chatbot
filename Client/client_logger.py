import os
from datetime import datetime

CLIENT_LOG_DIR = os.path.dirname(os.path.abspath(__file__))

ADMIN_LOG_FILE = os.path.join(CLIENT_LOG_DIR, "admin_client.log")
USER_LOG_FILE = os.path.join(CLIENT_LOG_DIR, "user_client.log")


def log_client_event(user: str, event_type: str, status: str, details, is_admin: bool = False):
    import json
    log_file = ADMIN_LOG_FILE if is_admin else USER_LOG_FILE
    timestamp = datetime.utcnow().isoformat()
    # Auto pretty-print details if it's dict/list or JSON string
    formatted_details = None
    if isinstance(details, (dict, list)):
        formatted_details = json.dumps(details, indent=2, ensure_ascii=False)
    elif isinstance(details, str):
        try:
            parsed = json.loads(details)
            formatted_details = json.dumps(parsed, indent=2, ensure_ascii=False)
        except Exception:
            formatted_details = details
    else:
        formatted_details = str(details)
    # Indent multiline details for log readability
    details_lines = formatted_details.split('\n')
    if len(details_lines) > 1:
        formatted_details = details_lines[0] + '\n' + '\n'.join('    ' + line for line in details_lines[1:])
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] user={user} event={event_type} status={status} details={formatted_details}\n") 