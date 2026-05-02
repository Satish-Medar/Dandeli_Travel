import json
from .config import BOOKINGS_PATH

# Fallback local store if Mongo is missing
_local_bookings = []
_local_loaded = False

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
        if not _local_loaded:
            ensure_bookings_store()
            with BOOKINGS_PATH.open("r", encoding="utf-8") as file:
                _local_bookings = json.load(file)
            _local_loaded = True
        return _local_bookings

def save_bookings(bookings: list[dict]) -> None:
    from travel_api.store import get_db
    db = get_db()
    if db is not None:
        collection = db.booking_requests
        for b in bookings:
            collection.update_one({"booking_id": b["booking_id"]}, {"$set": b}, upsert=True)
    else:
        global _local_bookings
        _local_bookings = bookings
        ensure_bookings_store()
        with BOOKINGS_PATH.open("w", encoding="utf-8") as file:
            json.dump(bookings, file, indent=2)

def next_booking_id(bookings: list[dict]) -> str:
    from travel_api.store import get_db
    db = get_db()
    if db is not None:
        count = db.booking_requests.count_documents({})
        return f"BK-{count + 1:04d}"
    return f"BK-{len(bookings) + 1:04d}"
