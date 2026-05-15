# Fire Dispatcher Backend

A FastAPI backend for a Lebanese Civil Defense fire/EMS/rescue dispatcher system.

The system supports live call transcription, offline post-call processing, incident generation, localization, database storage, and a Streamlit dashboard frontend.

## Stack

- FastAPI
- SQLAlchemy ORM + PostgreSQL
- Alembic migrations
- OpenAI agents
- ChromaDB for retrieval
- Streamlit dashboard
- Whisper / SimulStreaming bridge
- Docker Compose

## Repositories

This project is split across three parts:

1. **Main backend repository**  
   This repository.

2. **Dashboard frontend**  
   Download inside the backend repository:

   ```bash
   git clone https://github.com/taline-zeidan/fire-dispatch-dashboard
   ```

3. **SimulStreaming / Whisper bridge**  
   This can be downloaded anywhere on your machine:

   ```bash
   git clone https://github.com/MRIT03/SimulStreaming
   ```

## Recommended project structure

Recommended layout:

```text
fire-dispatch-backend/
├── app/
├── agents_service/
├── alembic/
├── docker-compose.yml
├── .env
├── fire-dispatch-dashboard/
│   └── ...
└── README.md
```

The SimulStreaming repository can be outside this folder:

```text
SimulStreaming/
├── tcp_server.py
├── simulstreaming_whisper_server.py
├── simulstreaming_whisper.py
└── ...
```

## Environment setup

Create a `.env` file:

```bash
cp .env.example .env
```

Set at least:

```env
OPENAI_API_KEY=your_api_key_here
```

If the dashboard runs in Docker and the bridge runs on your host machine, use:

```env
BRIDGE_CONTROL_URL=http://host.docker.internal:5003
```

If both the dashboard and bridge run directly on the same machine, use:

```env
BRIDGE_CONTROL_URL=http://localhost:5003
```

## Running the project

### 1. Clone the backend

```bash
git clone <this-repo-url>
cd <this-repo-folder>
```

### 2. Clone the dashboard inside the backend repo

```bash
git clone https://github.com/taline-zeidan/fire-dispatch-dashboard
```

### 3. Clone SimulStreaming

This does not need to be inside the backend repository:

```bash
git clone https://github.com/MRIT03/SimulStreaming
```

### 4. Start backend, agents service, database, and dashboard

From the backend repository:

```bash
docker compose up --build
```

This starts the PostgreSQL database and application services.

### 5. Run database migrations

In another terminal, run:

```bash
docker compose exec api alembic upgrade head
```

If your backend service is not named `api`, check the service names with:

```bash
docker compose ps
```

Then replace `api` with the correct backend service name.

### 6. Start the bridge

Wait around 5 seconds after Docker services start. Then open a terminal inside the SimulStreaming repository and run:

```bash
python tcp_server.py
```

The bridge connects to:

- port `5001` for live transcripts
- port `5002` for offline transcripts
- port `5003` for frontend end-call control

## Main services

- FastAPI backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Streamlit dashboard: usually `http://localhost:8501`
- Bridge control server: `http://localhost:5003`

## Main endpoints

- `GET /api/v1/health`
- `GET /api/v1/settings`
- `PUT /api/v1/settings`
- `GET /api/v1/incidents`
- `POST /api/v1/incidents`
- `PATCH /api/v1/incidents/{incident_id}`
- `GET /api/v1/transcripts/live`
- `DELETE /api/v1/transcripts/live`
- `POST /api/v1/transcripts/live/end`
- `GET /api/v1/transcripts/live/incident`
- `GET /api/v1/transcripts/audio/{filename}`
- `POST /api/v1/assistant/query`
- `POST /api/v1/assistant/knowledge`

## Bridge performance modes

The dashboard settings page allows selecting a performance mode.

### High performance

Streaming Whisper and offline Whisper may run in parallel.

Use this when the machine has enough CPU/GPU resources.

### Moderate performance

Streaming Whisper pauses while offline Whisper runs.

Use this when hardware resources are limited.

## Typical workflow

1. Start Docker services:

   ```bash
   docker compose up --build
   ```

2. Run migrations:

   ```bash
   docker compose exec api alembic upgrade head
   ```

3. Start the bridge from the SimulStreaming repository:

   ```bash
   python tcp_server.py
   ```

4. Open the dashboard.

5. Use the Live Dispatch page to monitor live transcripts.

6. Press **End Call** when the call is done.

7. The bridge finalizes the WAV file, runs offline Whisper, and sends the final transcript to the backend.

8. The backend runs the agent pipeline:

   - transcript cleaning
   - localization
   - incident record generation
   - database write

9. Review the generated incident in the dashboard.

## Database notes

PostgreSQL is started by Docker Compose.

Tables are managed through Alembic migrations. After starting the Docker services, run:

```bash
docker compose exec api alembic upgrade head
```

If you reset or remove the database volume, run the migration command again.

## Troubleshooting

### End Call button does not work

Make sure `tcp_server.py` is running.

The bridge should print something similar to:

```text
[Control] Listening on 0.0.0.0:5003
```

If the dashboard runs in Docker and the bridge runs on Windows, `localhost:5003` from inside the dashboard container will not point to the Windows host. Use:

```env
BRIDGE_CONTROL_URL=http://host.docker.internal:5003
```

If both the dashboard and bridge run directly on the same machine, use:

```env
BRIDGE_CONTROL_URL=http://localhost:5003
```

### Settings endpoint returns 404

Make sure the settings router is registered in the backend router:

```python
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
```

Then rebuild the backend:

```bash
docker compose down
docker compose up --build
```

### Database tables are missing

Run:

```bash
docker compose exec api alembic upgrade head
```

### OpenAI agent features fail

Make sure `OPENAI_API_KEY` is set in `.env`.

## Notes

- The bridge must be running for live transcription and end-call finalization.
- The backend and dashboard can be run through Docker Compose.
- The SimulStreaming bridge is run separately using Python.
- The dashboard settings page controls bridge performance mode through the backend settings API.
- `AUTO_CREATE_TABLES=true` can be useful for local development, but Alembic migrations are the preferred workflow.
