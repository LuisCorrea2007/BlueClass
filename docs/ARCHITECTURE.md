# MEMORA AI architecture

```text
Android Share Intent ─┐
Chrome Extension ─────┼── HTTPS + Bearer token ── FastAPI ── SQLAlchemy ── PostgreSQL
Web Dashboard ────────┘                              │
                                                    ├── Memory CRUD / search
                                                    ├── Agent context retrieval (lexical)
                                                    └── Skills / Markdown + ZIP export
```

## Current technology choices

- API: Python 3.12, FastAPI, Pydantic v2, Uvicorn.
- Persistence: PostgreSQL 16, SQLAlchemy 2, psycopg 3.
- Schema lifecycle: Alembic migrations.
- Packaging: Docker image and Docker Compose v2.
- Web: semantic HTML, CSS, vanilla JavaScript; no frontend framework runtime.
- Android: Kotlin native companion with encrypted local persistence.
- Browser capture: Chrome Manifest V3 extension, explicit user action.

## Retrieval and neural-network claims

The agent context endpoint currently performs lexical ranking. The dashboard graph is a visualization of memory/skill entities and their relationships. Neither is a trained neural network or vector embedding index. Semantic retrieval is a separate future capability and must be benchmarked against a relevance dataset before being enabled by default.

## Security boundary

The backend currently uses a shared bearer token when configured. This is suitable only for a controlled single-owner deployment behind HTTPS and strict access controls. It is not a multi-tenant identity system. Do not expose it as a public SaaS until user identity, per-tenant authorization, audit, rate limiting, retention/deletion policies and independent security review are implemented.
