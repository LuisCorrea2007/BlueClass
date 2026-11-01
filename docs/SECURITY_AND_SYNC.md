# Security and synchronization

## Implemented in this foundation
- Android stores local memory data and API settings using AndroidX EncryptedSharedPreferences.
- Android captures content only when the user explicitly shares it with the app.
- Mobile sync uses HTTPS and an optional bearer token.
- Android upload retries are idempotent using the client UUID in source_ref.
- Backend can require a bearer token by setting MEMORA_API_TOKEN.
- Production mode refuses to start without a configured API token.
- Browser extension captures visible conversation text only after the user clicks Save.

## Deployment requirements
- Deploy the API behind HTTPS.
- Set MEMORA_ENV=production, MEMORA_API_TOKEN, and MEMORA_DATABASE_URL.
- Use a managed PostgreSQL database and keep its credentials in the hosting provider's secret manager.
- Do not commit API tokens, database credentials, signing keys, or personal conversation exports.
- Configure database backups, retention, account-level authorization, rate limits, audit events, and tenant isolation before multi-user production use.

## Known limitations
The current bearer token is a shared service gate, not user identity or tenant isolation. The initial retrieval endpoint uses lexical matching, not embeddings. Browser extension selectors may need maintenance as AI sites change their UI. OAuth-based provider integrations, deletion propagation, and conflict resolution are not yet implemented.
