# Credential-ready deployment

ORPHEUS has two intentionally separate modes.

## 1. Local mode — no credentials and no cloud spending

```powershell
Copy-Item .env.example .env
powershell -ExecutionPolicy Bypass -File deployment/test-local.ps1
```

The deterministic simulator, verifier, catalog tools, API, and tests work in this mode. `ORPHEUS_LLM_BACKEND=mock` guarantees that no model request is sent.

## 2. Google Cloud mode — activate after the credit is redeemed

The recommended hackathon backend is Vertex AI. It uses Application Default Credentials locally and the Cloud Run service account after deployment; no API key is stored in the repository.

```powershell
gcloud auth login
gcloud auth application-default login
powershell -ExecutionPolicy Bypass -File deployment/prepare-cloud.ps1 -ProjectId YOUR_PROJECT_ID
powershell -ExecutionPolicy Bypass -File deployment/deploy-cloud-run.ps1 -ProjectId YOUR_PROJECT_ID -Public
```

The preparation script enables APIs, creates a dedicated runtime service account, creates the Pub/Sub topic and artifact bucket, initializes Firestore if necessary, grants runtime roles, and writes a non-secret `.env.cloud.generated` file.

## Optional Gemini API-key mode

For a lightweight local model test before Vertex AI is available:

```powershell
$env:ORPHEUS_LLM_BACKEND="gemini_api"
$env:GEMINI_API_KEY="YOUR_KEY"
$env:ORPHEUS_MODEL="gemini-3.6-flash"
```

Never commit `.env`, `.env.cloud.generated`, API keys, service-account JSON files, or access tokens.

## What still requires a real Google account

Code can be completed without credits, but these actions cannot be truthfully pre-validated offline:

1. redeeming the promotional credit;
2. linking billing to the chosen Google Cloud project;
3. confirming that the selected Gemini model is enabled in that project/region;
4. performing the first real Cloud Run and Vertex AI request;
5. capturing Cloud Console and logs for the demo video.
