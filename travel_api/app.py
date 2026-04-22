import asyncio
import json
import re
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
# trigger reload 2
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .models import AppConfig, AssistantReplyRequest, AssistantReplyResponse, ChatRequest, ChatResponse, MessageRecord, SessionCreateRequest, SessionDetail, SessionResponse, SessionSummary
from .services import app_config_payload, invoke_assistant, invoke_assistant_from_turns, list_user_sessions, record_message
from .store import DEFAULT_USER_ID, clear_session, get_or_create_session, get_session as load_session, normalize_user_id, persist_session, sync_user_profile, utc_now

BASE_DIR = Path(r"d:\RAG\CollegeProject")
FRONTEND_OUT_DIR = BASE_DIR / "frontend" / "out"
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"
NEXT_ASSET_DIR = FRONTEND_OUT_DIR / "_next"
VITE_ASSET_DIR = FRONTEND_DIST_DIR / "assets"

app = FastAPI(title="Dandeli Travel Assistant API", version="0.2.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if NEXT_ASSET_DIR.exists():
    app.mount("/_next", StaticFiles(directory=NEXT_ASSET_DIR), name="next-assets")
if VITE_ASSET_DIR.exists():
    app.mount("/assets", StaticFiles(directory=VITE_ASSET_DIR), name="assets")


@app.get("/config", response_model=AppConfig)
def app_config():
    return app_config_payload()


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/")
def serve_frontend():
    next_index_path = FRONTEND_OUT_DIR / "index.html"
    if next_index_path.exists():
        return FileResponse(next_index_path)
    vite_index_path = FRONTEND_DIST_DIR / "index.html"
    if vite_index_path.exists():
        return FileResponse(vite_index_path)
    raise HTTPException(status_code=503, detail="Frontend build not found. Run the frontend build first.")


@app.get("/sessions", response_model=list[SessionSummary])
def list_sessions(user_id: str = Query(default=DEFAULT_USER_ID)):
    return list_user_sessions(normalize_user_id(user_id))


@app.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session_detail(session_id: str, user_id: str = Query(default=DEFAULT_USER_ID)):
    session = load_session(normalize_user_id(user_id), session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionDetail(session_id=session_id, title=session.get("title", "New conversation"), updated_at=session.get("updated_at", utc_now()), messages=[MessageRecord(**item) for item in session.get("messages", [])])


@app.post("/sessions", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest):
    user_id = normalize_user_id(payload.user_id)
    sync_user_profile(user_id, payload.user_name, payload.user_email)
    session_id, session = get_or_create_session(user_id, None, payload.title)
    return SessionResponse(session_id=session_id, message="Session created.", title=session.get("title", "New conversation"))


@app.delete("/sessions/{session_id}", response_model=SessionResponse)
def reset_session(session_id: str, user_id: str = Query(default=DEFAULT_USER_ID)):
    session = clear_session(normalize_user_id(user_id), session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionResponse(session_id=session_id, message="Session cleared.", title=session["title"])


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_id = normalize_user_id(request.user_id)
    sync_user_profile(user_id, request.user_name, request.user_email)
    session_id, session = get_or_create_session(user_id, request.session_id)
    user_message = request.message.strip()
    record_message(session, "user", user_message)
    try:
        reply, node_name = invoke_assistant(session, user_message)
    except Exception:
        session["messages"].pop()
        reply, node_name = "I'm having trouble reaching one of the AI services right now. Please try again in a moment.", "System"
    record_message(session, "assistant", reply, node_name)
    persist_session(user_id, session_id, session)
    return ChatResponse(session_id=session_id, reply=reply)


@app.post("/assistant/reply", response_model=AssistantReplyResponse)
def assistant_reply(request: AssistantReplyRequest):
    try:
        reply, node_name = invoke_assistant_from_turns(request.messages, request.message.strip())
    except Exception:
        reply = "I'm having trouble reaching one of the AI services right now. Please try again in a moment."
    return AssistantReplyResponse(reply=reply)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    user_id = normalize_user_id(request.user_id)
    sync_user_profile(user_id, request.user_name, request.user_email)
    session_id, session = get_or_create_session(user_id, request.session_id)
    user_message = request.message.strip()
    record_message(session, "user", user_message)
    try:
        reply, node_name = invoke_assistant(session, user_message)
    except Exception:
        session["messages"].pop()
        reply, node_name = "I'm having trouble reaching one of the AI services right now. Please try again in a moment.", "System"
    record_message(session, "assistant", reply, node_name)
    persist_session(user_id, session_id, session)

    async def event_generator():
        yield f"event: session\ndata: {session_id}\n\n"
        for token in re.findall(r"\S+\s*|\n", reply) or [reply]:
            yield f"event: chunk\ndata: {json.dumps(token)}\n\n"
            await asyncio.sleep(0.012)
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
