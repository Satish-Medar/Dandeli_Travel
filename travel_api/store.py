import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

CHAT_STORE_PATH = Path(r"d:\RAG\CollegeProject\data\json_files\chat_sessions.json")
DEFAULT_USER_ID = "guest-local"


def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def normalize_user_id(user_id: str | None) -> str:
    cleaned = (user_id or "").strip()
    return cleaned or DEFAULT_USER_ID


def load_store() -> dict:
    CHAT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not CHAT_STORE_PATH.exists():
        CHAT_STORE_PATH.write_text("{}", encoding="utf-8")
    with CHAT_STORE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_store(store: dict) -> None:
    CHAT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHAT_STORE_PATH.open("w", encoding="utf-8") as file:
        json.dump(store, file, indent=2)


def ensure_user_bucket(store: dict, user_id: str) -> dict:
    if user_id not in store:
        store[user_id] = {"sessions": {}}
    store[user_id].setdefault("sessions", {})
    return store[user_id]


def get_or_create_session(user_id: str, session_id: str | None, title: str | None = None) -> tuple[str, dict]:
    store = load_store()
    user_bucket = ensure_user_bucket(store, user_id)
    if session_id and session_id in user_bucket["sessions"]:
        return session_id, user_bucket["sessions"][session_id]
    new_session_id = str(uuid4())
    session = {"title": title or "New conversation", "updated_at": utc_now(), "messages": []}
    user_bucket["sessions"][new_session_id] = session
    save_store(store)
    return new_session_id, session


def persist_session(user_id: str, session_id: str, session: dict) -> None:
    store = load_store()
    ensure_user_bucket(store, user_id)["sessions"][session_id] = session
    save_store(store)


def get_session(user_id: str, session_id: str) -> dict | None:
    user_bucket = ensure_user_bucket(load_store(), user_id)
    return user_bucket["sessions"].get(session_id)


def list_sessions_for_user(user_id: str) -> dict[str, dict]:
    user_bucket = ensure_user_bucket(load_store(), user_id)
    return user_bucket["sessions"]


def clear_session(user_id: str, session_id: str) -> dict | None:
    store = load_store()
    user_bucket = ensure_user_bucket(store, user_id)
    session = user_bucket["sessions"].get(session_id)
    if not session:
        return None
    session["messages"] = []
    session["title"] = "New conversation"
    session["updated_at"] = utc_now()
    save_store(store)
    return session


def sync_user_profile(user_id: str, user_name: str | None = None, user_email: str | None = None) -> None:
    # Auth profile persistence moved to the Next.js/Node layer that owns MongoDB access.
    return None
