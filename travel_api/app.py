
import os
import re
import time
import logging
from collections import defaultdict
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('travel_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException, Query, Request
# trigger reload 2
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from .models import AppConfig, AssistantReplyRequest, AssistantReplyResponse, ChatRequest, ChatResponse, MessageRecord, SessionCreateRequest, SessionDetail, SessionResponse, SessionSummary
from .services import app_config_payload, invoke_assistant, invoke_assistant_from_turns, list_user_sessions, record_message
from .store import DEFAULT_USER_ID, clear_session, get_or_create_session, get_session as load_session, normalize_user_id, persist_session, sync_user_profile, utc_now

import jwt
from fastapi import Depends, Header
from travel_tools.data_validator import validate_resorts_on_startup

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))  # requests per window
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))  # window in seconds (1 hour)

# In-memory rate limiting store (use Redis in production)
rate_limit_store = defaultdict(list)

def check_rate_limit(client_id: str) -> bool:
    """Check if client has exceeded rate limit. Returns True if allowed, False if blocked."""
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW

    # Clean old requests
    rate_limit_store[client_id] = [req_time for req_time in rate_limit_store[client_id] if req_time > window_start]

    # Check if under limit
    if len(rate_limit_store[client_id]) < RATE_LIMIT_REQUESTS:
        rate_limit_store[client_id].append(now)
        return True
    return False

def get_client_identifier(request: Request) -> str:
    """Get client identifier from request (IP + User-Agent for basic fingerprinting)."""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("User-Agent", "unknown")
    return f"{client_ip}:{hash(user_agent) % 10000}"  # Simple hash to avoid storing full UA


def validate_session_id(session_id: str) -> str:
    """Validate and sanitize session ID from path parameter."""
    if not session_id or not isinstance(session_id, str):
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Remove any path traversal attempts
    session_id = session_id.replace('/', '').replace('\\', '').replace('..', '')

    # Validate format (alphanumeric, hyphens, underscores only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise HTTPException(status_code=400, detail="Session ID contains invalid characters")

    # Length check
    if len(session_id) > 100:
        raise HTTPException(status_code=400, detail="Session ID too long")

    return session_id


def validate_user_id_query(user_id: str) -> str:
    """Validate user ID from query parameter."""
    if not user_id or not isinstance(user_id, str):
        return DEFAULT_USER_ID

    # Remove potentially dangerous characters
    user_id = re.sub(r'[^a-zA-Z0-9_.-]', '', user_id)

    # Length check
    if len(user_id) > 100:
        raise HTTPException(status_code=400, detail="User ID too long")

    return user_id or DEFAULT_USER_ID


def sanitize_string_input(input_str: str, max_length: int = 1000, allow_html: bool = False) -> str:
    """Sanitize string input to prevent XSS and other attacks."""
    if not input_str or not isinstance(input_str, str):
        return ""

    # Remove null bytes and control characters
    input_str = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', input_str)

    # Remove path traversal attempts
    input_str = input_str.replace('..', '').replace('\\', '/')

    if not allow_html:
        # Remove HTML/script tags
        input_str = re.sub(r'<[^>]+>', '', input_str)

    # Limit consecutive whitespace
    input_str = re.sub(r'\s{3,}', ' ', input_str)

    # Length limit
    return input_str.strip()[:max_length]


def verify_clerk_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.split(" ")[1]
    try:
        # Get Clerk secret key for token verification
        clerk_secret = os.getenv("CLERK_SECRET_KEY")
        if not clerk_secret:
            raise HTTPException(status_code=500, detail="Authentication service not configured")

        # Verify JWT token with proper signature validation
        decoded = jwt.decode(token, clerk_secret, algorithms=["RS256", "HS256"])
        return decoded.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_OUT_DIR = BASE_DIR / "frontend" / "out"
FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"
NEXT_ASSET_DIR = FRONTEND_OUT_DIR / "_next"
VITE_ASSET_DIR = FRONTEND_DIST_DIR / "assets"

app = FastAPI(title="Vana AI API", version="0.2.0")

@app.on_event("startup")
async def startup_event():
    """Validate resort data on application startup."""
    try:
        validate_resorts_on_startup()
    except Exception as e:
        logger.error(f"Resort data validation failed: {e}")
        # In production, you might want to exit the application
        # raise e

# CORS configuration - supports both local and production origins
def get_cors_origins():
    # Allow configurable CORS origins via environment variable
    cors_env = os.getenv("CORS_ORIGINS", "")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    # Default local origins
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_origin_regex=r"https://.*\.(netlify|vercel)\.app",
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
def list_sessions(user_id: str = Query(default=DEFAULT_USER_ID), auth_user_id: str = Depends(verify_clerk_user)):
    final_user_id = auth_user_id or validate_user_id_query(user_id)
    return list_user_sessions(final_user_id)


@app.get("/sessions/{session_id}", response_model=SessionDetail)
def get_session_detail(session_id: str, user_id: str = Query(default=DEFAULT_USER_ID), auth_user_id: str = Depends(verify_clerk_user)):
    # Validate session_id from path parameter
    validated_session_id = validate_session_id(session_id)
    final_user_id = auth_user_id or validate_user_id_query(user_id)

    session = load_session(final_user_id, validated_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionDetail(session_id=validated_session_id, title=session.get("title", "New conversation"), updated_at=session.get("updated_at", utc_now()), messages=[MessageRecord(**item) for item in session.get("messages", [])])


@app.post("/sessions", response_model=SessionResponse)
def create_session(payload: SessionCreateRequest, auth_user_id: str = Depends(verify_clerk_user)):
    final_user_id = auth_user_id or normalize_user_id(payload.user_id)
    sync_user_profile(final_user_id, payload.user_name, payload.user_email)
    session_id, session = get_or_create_session(final_user_id, None, payload.title)
    return SessionResponse(session_id=session_id, message="Session created.", title=session.get("title", "New conversation"))


@app.delete("/sessions/{session_id}", response_model=SessionResponse)
def reset_session(session_id: str, user_id: str = Query(default=DEFAULT_USER_ID), auth_user_id: str = Depends(verify_clerk_user)):
    # Validate session_id from path parameter
    validated_session_id = validate_session_id(session_id)
    final_user_id = auth_user_id or validate_user_id_query(user_id)

    session = clear_session(final_user_id, validated_session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionResponse(session_id=validated_session_id, message="Session cleared.", title=session["title"])


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, auth_user_id: str = Depends(verify_clerk_user), req: Request = None):
    # Rate limiting check
    client_id = get_client_identifier(req)
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

    final_user_id = auth_user_id or normalize_user_id(request.user_id)
    sync_user_profile(final_user_id, request.user_name, request.user_email)
    session_id, session = get_or_create_session(final_user_id, request.session_id)
    user_message = request.message.strip()

    # Additional validation for message content
    if len(user_message) > 10000:
        raise HTTPException(status_code=400, detail="Message too long (max 10000 characters)")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    record_message(session, "user", user_message)
    try:
        reply, node_name = await invoke_assistant(session, user_message)
    except Exception as e:
        # Remove the failed user message from session
        if session["messages"]:
            session["messages"].pop()
        # Log the actual error for debugging
        logger.error(f"Assistant invocation failed: {str(e)}")
        reply, node_name = "I'm having trouble reaching one of the AI services right now. Please try again in a moment.", "System"
    record_message(session, "assistant", reply, node_name)
    persist_session(final_user_id, session_id, session)
    return ChatResponse(session_id=session_id, reply=reply)


@app.post("/assistant/reply", response_model=AssistantReplyResponse)
async def assistant_reply(request: AssistantReplyRequest):
    # Additional validation for assistant reply endpoint
    if len(request.messages) > 50:
        raise HTTPException(status_code=400, detail="Too many conversation turns (max 50)")

    message = request.message.strip()
    if len(message) > 10000:
        raise HTTPException(status_code=400, detail="Message too long (max 10000 characters)")
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        reply, node_name = await invoke_assistant_from_turns(request.messages, message)
    except Exception as e:
        # Log the actual error for debugging
        logger.error(f"Assistant reply failed: {str(e)}")
        reply = "I'm having trouble reaching one of the AI services right now. Please try again in a moment."
        node_name = "System"
    return AssistantReplyResponse(reply=reply, node_name=node_name)


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, auth_user_id: str = Depends(verify_clerk_user), req: Request = None):
    # Rate limiting check
    client_id = get_client_identifier(req)
    if not check_rate_limit(client_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")

    import asyncio
    import json
    import re
    final_user_id = auth_user_id or normalize_user_id(request.user_id)
    sync_user_profile(final_user_id, request.user_name, request.user_email)
    session_id, session = get_or_create_session(final_user_id, request.session_id)
    user_message = request.message.strip()

    # Additional validation for streaming endpoint
    if len(user_message) > 10000:
        raise HTTPException(status_code=400, detail="Message too long (max 10000 characters)")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    record_message(session, "user", user_message)
    try:
        reply, node_name = await invoke_assistant(session, user_message)
    except Exception as e:
        # Remove the failed user message from session
        if session["messages"]:
            session["messages"].pop()
        # Log the actual error for debugging
        logger.error(f"Streaming assistant invocation failed: {str(e)}")
        reply, node_name = "I'm having trouble reaching one of the AI services right now. Please try again in a moment.", "System"
    record_message(session, "assistant", reply, node_name)
    persist_session(final_user_id, session_id, session)

    async def event_generator():
        yield f"event: session\ndata: {session_id}\n\n"
        for token in re.findall(r"\S+\s*|\n", reply) or [reply]:
            yield f"event: chunk\ndata: {json.dumps(token)}\n\n"
            await asyncio.sleep(0.012)
        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/validate/data")
async def validate_data():
    """Validate resort data integrity."""
    from travel_tools.data_validator import load_and_validate_resorts
    from pathlib import Path

    base_dir = Path(__file__).resolve().parent.parent
    resorts_file = base_dir / "data" / "json_files" / "resorts.json"

    try:
        data, is_valid, errors = load_and_validate_resorts(resorts_file)

        return {
            "valid": is_valid,
            "total_resorts": len(data),
            "errors": errors[:50],  # Limit error output
            "error_count": len(errors)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")
