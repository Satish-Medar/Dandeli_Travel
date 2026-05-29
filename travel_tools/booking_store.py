# Stores and retrieves booking records for the reservation workflow.
# File: travel_tools/booking_store.py

# Simple overview:
# - This module loads and saves booking records.
# - It uses MongoDB when configured, and falls back to local JSON storage.
# - This keeps booking persistence separate from the business logic.


import json
import threading
import uuid
from datetime import datetime
from .config import BOOKINGS_PATH

# Fallback local store if Mongo is missing
_local_bookings = []
_local_loaded = False
_lock = threading.Lock()

# Make sure the local bookings JSON file exists.
def ensure_bookings_store() -> None:
    BOOKINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not BOOKINGS_PATH.exists():
        BOOKINGS_PATH.write_text("[]", encoding="utf-8")

# Load all bookings from MongoDB if available, otherwise use the local JSON fallback.
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

# Save booking records to the configured database or the local JSON file.
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

class BookingStore:
    """Simple in-memory booking store used for tests and local fallback."""

    def __init__(self):
        self._bookings = load_bookings() or []

    def save_booking(self, booking_data: dict) -> dict:
        booking_id = next_booking_id()
        booking = {
            "booking_id": booking_id,
            "resort": booking_data.get("resort"),
            "dates": booking_data.get("dates"),
            "guests": booking_data.get("guests"),
            "contactInfo": booking_data.get("contactInfo"),
            "status": "confirmed",
            "created_at": datetime.now().isoformat(timespec="seconds")
        }
        self._bookings.append(booking)
        save_bookings(self._bookings)
        return booking

    def get_status(self, booking_id: str) -> str | None:
        for booking in self._bookings:
            if booking.get("booking_id") == booking_id:
                return booking.get("status")
        return None


def next_booking_id(bookings: list[dict] = None) -> str:
    """Generate a unique thread-safe booking ID."""
    return f"BK-{str(uuid.uuid4())[:8].upper()}"