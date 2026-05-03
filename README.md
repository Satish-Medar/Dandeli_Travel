# Vana AI Agent

An intelligent travel assistant for Dandeli resort search, planning, comparison, and booking assistance.

## Tech Stack

- Frontend: Next.js 15, React 18, Clerk auth
- Backend: FastAPI, Uvicorn
- AI: LangGraph multi-agent orchestrator
- Search: Pinecone vector retrieval + local JSON fallback
- LLMs: Google Gemini Generative AI and Groq Llama instant

## What was improved

- Lazy vector store initialization to avoid backend startup hang
- Local JSON resort fallback when Pinecone / Chroma is unavailable
- Cleaner search routing and filter extraction
- Robust backend health check and frontend proxy support
- Better run/test documentation for local and Docker workflows

## Prerequisites

- Python 3.11+
- Node.js 20+ and npm
- Docker & Docker Compose (optional for containerized setup)

## Local development

### 1. Prepare Python environment

```bash
cd D:/RAG/CollegeProject
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # PowerShell
# or .\.venv\Scripts\activate.bat for cmd
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Configure environment

- Copy `.env.example` to `.env`
- Fill values for:
  - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
  - `CLERK_SECRET_KEY`
  - `GROQ_API_KEY` or `GOOGLE_API_KEY`
  - `MONGODB_URI`
  - Optional Twilio values for booking notifications
  - Optional Pinecone values for vector search

### 3. Start backend

```bash
python -m uvicorn travel_api.app:app --reload --host 0.0.0.0 --port 8000
```

- If port `8000` is already taken, use `--port 8001` and set `NEXT_PUBLIC_API_URL=http://127.0.0.1:8001`

### 4. Start frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Verify startup

- Backend health: `http://127.0.0.1:8000/health`
- Frontend: `http://127.0.0.1:3000`

## Docker setup

```bash
docker compose up --build
```

- Frontend connects to backend through `NEXT_PUBLIC_API_URL=http://api:8000`
- Backend health is checked automatically by Docker Compose

## Testing manually

### Backend health

```bash
curl http://127.0.0.1:8000/health
```

### Local search fallback

```bash
python -c "from travel_tools.search_engine import load_all_documents; docs=load_all_documents(); print('documents', len(docs))"
```

### API smoke test

```bash
curl -X GET http://127.0.0.1:8000/config
```

## Optional ingestion

- Use `ingest.py` to rebuild the Pinecone index from `data/json_files/resorts.json`

```bash
python ingest.py
```

## Notes

- If Pinecone is not configured, the backend uses local resort JSON data.
- Local frontend proxy uses `NEXT_PUBLIC_API_URL` from `frontend/next.config.mjs`.
- The backend now avoids import-time blocking when initializing external vector stores.
