import uuid
from datetime import datetime

def generate_id() -> str:
    return str(uuid.uuid4())

def current_timestamp() -> datetime:
    return datetime.utcnow()
