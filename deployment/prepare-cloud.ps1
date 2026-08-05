param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$ServiceAccountName = "orpheus-runtime"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    throw "Google Cloud CLI (gcloud) is not installed or is not on PATH."
}

$ServiceAccount = "$ServiceAccountName@$ProjectId.iam.gserviceaccount.com"
$Bucket = "$ProjectId-orpheus-artifacts"
$Topic = "orpheus-mission-events"

Write-Host "Configuring project $ProjectId..."
gcloud config set project $ProjectId | Out-Null

gcloud services enable `
    aiplatform.googleapis.com `
    run.googleapis.com `
    cloudbuild.googleapis.com `
    artifactregistry.googleapis.com `
    firestore.googleapis.com `
    pubsub.googleapis.com `
    storage.googleapis.com `
    secretmanager.googleapis.com `
    logging.googleapis.com

$ExistingSa = gcloud iam service-accounts list --filter="email=$ServiceAccount" --format="value(email)"
if (-not $ExistingSa) {
    gcloud iam service-accounts create $ServiceAccountName --display-name="ORPHEUS runtime"
}

$Roles = @(
    "roles/aiplatform.user",
    "roles/datastore.user",
    "roles/pubsub.publisher",
    "roles/storage.objectAdmin",
    "roles/logging.logWriter"
)
foreach ($Role in $Roles) {
    gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$ServiceAccount" `
        --role=$Role `
        --condition=None | Out-Null
}

$ExistingTopic = gcloud pubsub topics list --filter="name:$Topic" --format="value(name)"
if (-not $ExistingTopic) {
    gcloud pubsub topics create $Topic | Out-Null
}

$ExistingBucket = gcloud storage buckets list --filter="name:$Bucket" --format="value(name)"
if (-not $ExistingBucket) {
    gcloud storage buckets create "gs://$Bucket" --location=$Region --uniform-bucket-level-access
}

try {
    gcloud firestore databases describe --database="(default)" | Out-Null
} catch {
    gcloud firestore databases create --database="(default)" --location=$Region --type=firestore-native
}

@"
ORPHEUS_RUNTIME_MODE=google_cloud
ORPHEUS_LLM_BACKEND=vertex_ai
ORPHEUS_MODEL=gemini-3.6-flash
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=$ProjectId
GOOGLE_CLOUD_LOCATION=global
ORPHEUS_FIRESTORE_ENABLED=true
ORPHEUS_FIRESTORE_COLLECTION=orpheus_missions
ORPHEUS_PUBSUB_ENABLED=true
ORPHEUS_PUBSUB_TOPIC=$Topic
ORPHEUS_STORAGE_ENABLED=true
ORPHEUS_STORAGE_BUCKET=$Bucket
ORPHEUS_SERVICE_ACCOUNT=$ServiceAccount
"@ | Set-Content -Encoding UTF8 .env.cloud.generated

Write-Host "Cloud prerequisites prepared. Generated .env.cloud.generated without secrets."
