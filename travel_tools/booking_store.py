import json
import threading
import uuid
from .config import BOOKINGS_PATH

# Fallback local store if Mongo is missing
_local_bookings = []
_local_loaded = False
_lock = threading.Lock()

def ensure_bookings_store() -> None:
    BOOKINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not BOOKINGS_PATH.exists():
        BOOKINGS_PATH.write_text("[]", encoding="utf-8")

def load_bookings() -> list[dict]:
    from travel_api.store import get_db
    db = get_db()
    if db is not None:
        return list(db.booking_requests.find({}, {"_id": 0}))
    else:
        global _local_loaded, _local_bookings
        with _lock:
            if not _local_loaded:
                ensure_bookings_store()
                with BOOKINGS_PATH.open("r", encoding="utf-8") as file:
                    try:
                        _local_bookings = json.load(file)
                    except json.JSONDecodeError:
                        _local_bookings = []
                _local_loaded = True
            return _local_bookings.copy()

def save_bookings(bookings: list[dict]) -> None:
    from travel_api.store import get_db
    db = get_db()
    if db is not None:
        collection = db.booking_requests
        for b in bookings:
            collection.update_one({"booking_id": b["booking_id"]}, {"$set": b}, upsert=True)
    else:
        global _local_bookings
        with _lock:
            _local_bookings = bookings.copy()
            ensure_bookings_store()
            with BOOKINGS_PATH.open("w", encoding="utf-8") as file:
                json.dump(_local_bookings, file, indent=2)

def next_booking_id(bookings: list[dict] = None) -> str:
    """Generate a unique thread-safe booking ID."""
    return f"BK-{str(uuid.uuid4())[:8].upper()}"
