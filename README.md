# Fire Dispatcher Backend

A production-leaning FastAPI backend for a fire/EMS/rescue dispatcher project.

## Stack
- FastAPI
- SQLAlchemy ORM + PostgreSQL
- Alembic migrations
- LangChain + OpenAI
- ChromaDB for retrieval

## What is included
- Dispatcher user management
- Incident type catalog
- Incident tracking
- Call intake and linkage to dispatcher + incident
- Assistant endpoint for LLM-backed operational help
- Knowledge ingestion into ChromaDB
- Docker setup
- Initial Alembic migration

## Domain model summary
- **dispatchers**: users who handle calls
- **incident_types**: reusable taxonomy like structure fire, vehicle fire, EMS transport, rescue
- **incidents**: actual emergency events with type, location, severity, and status
- **calls**: incoming calls handled by a dispatcher and optionally linked to an incident

## Quick start

### 1) Create environment file
```bash
cp .env.example .env
```

Fill in `OPENAI_API_KEY` in `.env` if you want assistant features.

### 2) Start PostgreSQL
```bash
docker compose up -d db
```

### 3) Install Python dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 4) Run database migrations
```bash
alembic upgrade head
```

### 5) Start the API
```bash
uvicorn app.main:app --reload
```

Open docs at `http://127.0.0.1:8000/docs`

## Optional: start everything with Docker
```bash
docker compose up --build
```

## Main endpoints
- `GET /api/v1/health`
- `POST /api/v1/dispatchers`
- `GET /api/v1/dispatchers`
- `POST /api/v1/incident-types`
- `GET /api/v1/incident-types`
- `POST /api/v1/incidents`
- `PATCH /api/v1/incidents/{incident_id}/status`
- `POST /api/v1/calls`
- `GET /api/v1/calls`
- `POST /api/v1/assistant/query`
- `POST /api/v1/assistant/knowledge`

## Suggested frontend flow for Streamlit
1. Create/login dispatcher.
2. Create or fetch incident types.
3. Intake a call and assign the dispatcher.
4. Create incident if needed.
5. Link the call to that incident.
6. Ask the assistant for summary, next steps, or retrieval-augmented guidance.

## Notes
- The assistant routes gracefully fail with a clear message if `OPENAI_API_KEY` is not configured.
- `AUTO_CREATE_TABLES=true` can create tables at startup for local development, but migrations are the preferred workflow.
