# MEMORA AI Android
Native companion app for user-initiated capture through the Android Sharesheet.

## Features
- Receives shared plain text from supported apps.
- Stores memories locally using AndroidX EncryptedSharedPreferences.
- Works offline for capture.
- Uploads pending memories to a configured HTTPS FastAPI backend.
- Downloads remote memories during synchronization.
- Uses stable client UUIDs for idempotent upload retries.

## Configure
1. Deploy the FastAPI backend over HTTPS.
2. Enter its base URL in the app.
3. If MEMORA_API_TOKEN is configured on the server, enter the same bearer token.
4. Save connection settings, then tap Sync now.

The app does not silently scrape private content from other apps. Use the Android Share action explicitly.

## Release status
This is a debug build. A production Play Store release still requires release signing, key custody, privacy disclosures, full-device QA, and security review.