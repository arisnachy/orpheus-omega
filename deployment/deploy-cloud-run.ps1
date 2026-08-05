param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$ServiceName = "orpheus-omega",
    [string]$ServiceAccountName = "orpheus-runtime",
    [switch]$Public
)

$ErrorActionPreference = "Stop"
$ServiceAccount = "$ServiceAccountName@$ProjectId.iam.gserviceaccount.com"
$Bucket = "$ProjectId-orpheus-artifacts"
$AccessFlag = if ($Public) { "--allow-unauthenticated" } else { "--no-allow-unauthenticated" }
$Environment = @(
    "ORPHEUS_RUNTIME_MODE=google_cloud",
    "ORPHEUS_LLM_BACKEND=vertex_ai",
    "ORPHEUS_MODEL=gemini-3.6-flash",
    "GOOGLE_GENAI_USE_VERTEXAI=true",
    "GOOGLE_CLOUD_PROJECT=$ProjectId",
    "GOOGLE_CLOUD_LOCATION=global",
    "ORPHEUS_FIRESTORE_ENABLED=true",
    "ORPHEUS_FIRESTORE_COLLECTION=orpheus_missions",
    "ORPHEUS_PUBSUB_ENABLED=true",
    "ORPHEUS_PUBSUB_TOPIC=orpheus-mission-events",
    "ORPHEUS_STORAGE_ENABLED=true",
    "ORPHEUS_STORAGE_BUCKET=$Bucket"
) -join ","

gcloud config set project $ProjectId | Out-Null

gcloud run deploy $ServiceName `
    --source . `
    --project=$ProjectId `
    --region=$Region `
    --service-account=$ServiceAccount `
    --set-env-vars=$Environment `
    --memory=1Gi `
    --cpu=1 `
    --min-instances=0 `
    --max-instances=3 `
    $AccessFlag

Write-Host "Deployment complete. Verify /health, /readiness, and /missions/reference."
