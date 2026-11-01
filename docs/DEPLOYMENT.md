# MEMORA AI deployment guide (no Docker)

## 1. Database
Create a PostgreSQL database with a managed provider such as Neon. Copy the connection string and ensure it includes TLS (usually `sslmode=require`). MEMORA uses SQLAlchemy with psycopg 3.

## 2. API hosting
Use the included Render Blueprint (`render.yaml`) to create the Python web service. It runs:
```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```
No Docker image is required.

## 3. Required secrets
In the hosting service's environment settings configure:
- `MEMORA_ENV=production`
- `MEMORA_API_TOKEN`: a long random secret generated for this deployment.
- `MEMORA_DATABASE_URL`: the managed PostgreSQL connection string.

The service intentionally refuses to start in production without a token and persistent PostgreSQL. Never put secrets in source control or in public screenshots.

## 4. Connect Android
Install **MEMORA AI Sync** alongside the initial MEMORA app. Enter the deployed HTTPS API URL and the same bearer token, save the connection, and tap **Sync now**. The companion app uses encrypted local preferences and keeps local records if the server is unavailable.

## 5. Install browser extension
In desktop Chrome, open `chrome://extensions`, enable Developer mode, choose **Load unpacked**, and select the repository's `extension` folder. Open a ChatGPT, Claude, or Gemini conversation, reload the tab, then use the extension button to capture the visible conversation. Grant the requested server permission when connecting to your API.

## 6. Production gate
Before real multi-user use, implement per-user OAuth/OIDC, tenant-scoped database rows and authorization, migrations, backup/restore, deletion propagation, rate limiting, audit logging, privacy policy, and signed release APK distribution. The current API bearer token is a shared service credential and must not be treated as multi-tenant authentication.
