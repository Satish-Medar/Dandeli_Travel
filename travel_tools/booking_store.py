import json

from .config import BOOKINGS_PATH


def ensure_bookings_store() -> None:
    BOOKINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not BOOKINGS_PATH.exists():
        BOOKINGS_PATH.write_text("[]", encoding="utf-8")


def load_bookings() -> list[dict]:
    ensure_bookings_store()
    with BOOKINGS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_bookings(bookings: list[dict]) -> None:
    ensure_bookings_store()
    with BOOKINGS_PATH.open("w", encoding="utf-8") as file:
        json.dump(bookings, file, indent=2)


def next_booking_id(bookings: list[dict]) -> str:
    return f"BK-{len(bookings) + 1:04d}"
