# MEMORA AI roadmap

## Current foundation
- Native Android capture through Sharesheet.
- Encrypted local preferences and local-first save.
- HTTPS API sync with idempotent retries and cloud pull.
- FastAPI memory and skills endpoints.
- Web dashboard for memory and skill management.
- Chrome MV3 extension with explicit capture from ChatGPT, Claude and Gemini.
- Markdown and ZIP skill export.
- CI build for Android and backend tests.

## Next engineering milestones
1. Multi-user identity: OAuth/OIDC, user-scoped records, tenant isolation and authorization tests.
2. Durable production storage: managed PostgreSQL, migrations, backups and restore drills.
3. Better retrieval: embeddings, hybrid BM25/vector search, reranking and source citations.
4. Skills lifecycle: versioning, validation, import, signed share links and revocation.
5. Provider connections: official OAuth/API integrations where providers permit them; no silent scraping.
6. Sync correctness: deletion propagation, conflict policy, background sync and observability.
7. Release hardening: threat model, privacy policy, data export/deletion, signed release APK and device QA.
