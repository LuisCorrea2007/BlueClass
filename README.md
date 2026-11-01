# MEMORA AI

Provider-independent memory and portable skills foundation.

## Components
- **Android companion:** explicit Sharesheet capture, encrypted local storage, local-first saves, HTTPS upload and cloud pull.
- **FastAPI backend:** memory CRUD, conversation ingestion, skill library, Markdown/ZIP exports and ranked lexical context retrieval for AI agents.
- **Web dashboard:** browser-based memory and skills manager.
- **Chrome extension:** user-triggered capture of visible text from ChatGPT, Claude and Gemini.
- **CI:** Android APK build and backend pytest workflow.

## Repository
GitHub: https://github.com/LuisCorrea2007/BlueClass

## Android build
GitHub Actions builds a debug APK when Android source changes. Open the Actions tab and download the `memora-ai-debug-apk` artifact. Debug builds are for testing; Play Store distribution requires a separately signed release build.

## Backend deployment
A Render blueprint is provided in `render.yaml`. Configure a managed PostgreSQL connection as `MEMORA_DATABASE_URL` and a long random `MEMORA_API_TOKEN` in the host's secret settings. Set `MEMORA_ENV=production`. Do not commit secrets.

## Important security and product boundaries
MEMORA captures content only when the user explicitly shares it or clicks the browser extension. It does not silently read private chats in other apps. Provider API/OAuth integrations depend on each provider's permissions and terms.

This is an actively developed foundation, not yet a production-certified multi-tenant enterprise service. User accounts/OIDC, tenant isolation, vector retrieval, migrations, backup/restore, signed release keys, audit logs, deletion propagation and full security review remain outstanding. See `docs/ROADMAP.md`.
