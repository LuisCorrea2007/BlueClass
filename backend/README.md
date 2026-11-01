# MEMORA API

FastAPI service for memories, conversation ingestion, skill management, exports and agent context retrieval.

## Local run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open `http://127.0.0.1:8000` for the dashboard and `/docs` for API documentation.

## Environment
- `MEMORA_ENV=production` requires a configured `MEMORA_API_TOKEN`.
- `MEMORA_DATABASE_URL` accepts a SQLAlchemy URL. PostgreSQL is recommended for hosted use; SQLite is the development default.

## Endpoints
- `GET /api/health`
- `POST/GET /api/memories`
- `DELETE /api/memories/{id}`
- `POST /api/ingest/conversation`
- `GET /api/agents/context?q=...`
- `POST/GET /api/skills`
- `GET /api/skills/{id}/export?format=md|zip`

The initial retrieval is lexical. It is not yet an embedding/vector search engine. The bearer token is a shared service credential, not multi-user identity.
