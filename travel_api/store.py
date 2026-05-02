import os
from datetime import datetime
from uuid import uuid4
from pymongo import MongoClient

DEFAULT_USER_ID = "guest-local"

_client = None
_db = None

def get_db():
    global _client, _db
    if _db is not None:
        return _db
    
    mongo_uri = os.getenv("MONGODB_URI")
    if not mongo_uri:
        print("WARNING: MONGODB_URI not found. Using local memory store fallback for dev.")
        return None
        
    try:
        _client = MongoClient(mongo_uri)
        _db = _client.get_database("dandeli_travel")
        return _db
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None

# Local fallback for dev without Mongo
_local_store = {}

def utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def normalize_user_id(user_id: str | None) -> str:
    cleaned = (user_id or "").strip()
    return cleaned or DEFAULT_USER_ID

def ensure_user_bucket(user_id: str) -> dict:
    if user_id not in _local_store:
        _local_store[user_id] = {"sessions": {}}
    return _local_store[user_id]

def get_or_create_session(user_id: str, session_id: str | None, title: str | None = None) -> tuple[str, dict]:
    db = get_db()
    if db is not None:
        collection = db.chat_sessions
        if session_id:
            doc = collection.find_one({"user_id": user_id, "session_id": session_id})
            if doc:
                return session_id, {"title": doc.get("title", "New conversation"), "updated_at": doc.get("updated_at", utc_now()), "messages": doc.get("messages", [])}
        
        new_session_id = str(uuid4())
        session = {"title": title or "New conversation", "updated_at": utc_now(), "messages": []}
        collection.insert_one({"user_id": user_id, "session_id": new_session_id, **session})
        return new_session_id, session
    else:
        user_bucket = ensure_user_bucket(user_id)
        if session_id and session_id in user_bucket["sessions"]:
            return session_id, user_bucket["sessions"][session_id]
        new_session_id = str(uuid4())
        session = {"title": title or "New conversation", "updated_at": utc_now(), "messages": []}
        user_bucket["sessions"][new_session_id] = session
        return new_session_id, session

def persist_session(user_id: str, session_id: str, session: dict) -> None:
    db = get_db()
    if db is not None:
        db.chat_sessions.update_one(
            {"user_id": user_id, "session_id": session_id},
            {"$set": {"title": session.get("title"), "updated_at": utc_now(), "messages": session.get("messages", [])}},
            upsert=True
        )
    else:
        ensure_user_bucket(user_id)["sessions"][session_id] = session

def get_session(user_id: str, session_id: str) -> dict | None:
    db = get_db()
    if db is not None:
        doc = db.chat_sessions.find_one({"user_id": user_id, "session_id": session_id})
        if doc:
            return {"title": doc.get("title"), "updated_at": doc.get("updated_at"), "messages": doc.get("messages", [])}
        return None
    else:
        return ensure_user_bucket(user_id)["sessions"].get(session_id)

def list_sessions_for_user(user_id: str) -> dict[str, dict]:
    db = get_db()
    if db is not None:
        docs = db.chat_sessions.find({"user_id": user_id})
        return {doc["session_id"]: {"title": doc.get("title"), "updated_at": doc.get("updated_at"), "messages": doc.get("messages", [])} for doc in docs}
    else:
        return ensure_user_bucket(user_id)["sessions"]

def clear_session(user_id: str, session_id: str) -> dict | None:
    db = get_db()
    if db is not None:
        doc = db.chat_sessions.find_one({"user_id": user_id, "session_id": session_id})
        if not doc:
            return None
        session = {"title": "New conversation", "updated_at": utc_now(), "messages": []}
        db.chat_sessions.update_one({"user_id": user_id, "session_id": session_id}, {"$set": session})
        return session
    else:
        user_bucket = ensure_user_bucket(user_id)
        session = user_bucket["sessions"].get(session_id)
        if not session:
            return None
        session["messages"] = []
        session["title"] = "New conversation"
        session["updated_at"] = utc_now()
        return session

def sync_user_profile(user_id: str, user_name: str | None = None, user_email: str | None = None) -> None:
    # Auth profile persistence handled by Next.js or via separate collection
    db = get_db()
    if db is not None and user_email:
        db.users.update_one(
            {"user_id": user_id},
            {"$set": {"user_name": user_name, "user_email": user_email, "last_active": utc_now()}},
            upsert=True
        )
    return None
