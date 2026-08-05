# ORPHEUS Ω autonomous operation

## Two execution modes

### Local or persistent server

When `ORPHEUS_AUTONOMY_ENABLED=true`, FastAPI starts an in-process loop. It performs a cycle immediately and repeats according to `ORPHEUS_AUTONOMY_INTERVAL_SECONDS`.

This mode is suitable for a local workstation, VM, or container that remains alive.

### Cloud Run serverless mode

Cloud Run instances may scale to zero, so an in-process timer alone is not a reliable 24/7 scheduler. The deployment therefore sets `ORPHEUS_AUTONOMY_ENABLED=false` and uses Cloud Scheduler to invoke `POST /autonomy/cycle` on a cron schedule.

After deploying the service, configure the scheduler:

```powershell
powershell -ExecutionPolicy Bypass -File deployment/configure-autonomy-scheduler.ps1 `
  -ProjectId YOUR_PROJECT_ID `
  -Schedule "*/30 * * * *"
```

The script:

- enables Cloud Scheduler, IAM, and Cloud Run APIs;
- creates or reuses a scheduler service account;
- grants it the Cloud Run Invoker role;
- discovers the deployed service URL;
- creates or updates the scheduled HTTP job;
- uses an OIDC token for authenticated invocation;
- targets the autonomous-cycle endpoint.

Test it manually:

```powershell
gcloud scheduler jobs run orpheus-omega-autonomous-cycle `
  --location=us-central1 `
  --project=YOUR_PROJECT_ID
```

## What autonomy means here

ORPHEUS automatically performs safe, local, reversible work:

- mission-contract definition;
- deterministic simulation;
- independent verification;
- beneficiary mapping;
- opportunity ranking;
- pricing, cost, margin, licensing, and funding hypotheses;
- evidence-package preparation;
- field-validation protocol design;
- provenance and limitation recording.

It does not automatically perform external or irreversible work. These remain in the approval queue:

- contacting a person or organization;
- publishing an offer or claim;
- signing or changing a contract;
- spending or accepting money;
- modifying accounts or credentials;
- exposing private information;
- making legal, patent, safety, or regulatory representations.

## Current boundary

The autonomous opportunity planner presently derives opportunity hypotheses from verified repository evidence. Live partner, grant, market, patent, and customer discovery requires an authenticated external-search connector and authoritative source capture. Until that connector is enabled, the interface labels commercial figures as hypotheses rather than confirmed opportunities.

## Runtime endpoints

- `GET /autonomy/state`
- `POST /autonomy/start`
- `POST /autonomy/stop`
- `POST /autonomy/cycle`
- `POST /autonomy/profile`
- `POST /autonomy/approve/{action_id}`
- `POST /chat`
