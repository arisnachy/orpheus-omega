param(
    [Parameter(Mandatory = $true)][string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$SchedulerRegion = "us-central1",
    [string]$ServiceName = "orpheus-omega",
    [string]$InvokerServiceAccountName = "orpheus-scheduler",
    [string]$Schedule = "*/30 * * * *",
    [string]$TimeZone = "America/Santo_Domingo"
)

$ErrorActionPreference = "Stop"
$ServiceAccount = "$InvokerServiceAccountName@$ProjectId.iam.gserviceaccount.com"
$JobName = "$ServiceName-autonomous-cycle"

gcloud config set project $ProjectId | Out-Null

gcloud services enable `
    run.googleapis.com `
    cloudscheduler.googleapis.com `
    iam.googleapis.com `
    --project=$ProjectId | Out-Null

$ExistingServiceAccount = gcloud iam service-accounts describe $ServiceAccount `
    --project=$ProjectId `
    --format="value(email)" 2>$null

if (-not $ExistingServiceAccount) {
    gcloud iam service-accounts create $InvokerServiceAccountName `
        --project=$ProjectId `
        --display-name="ORPHEUS autonomous scheduler" | Out-Null
}

gcloud run services add-iam-policy-binding $ServiceName `
    --project=$ProjectId `
    --region=$Region `
    --member="serviceAccount:$ServiceAccount" `
    --role="roles/run.invoker" | Out-Null

$ServiceUrl = gcloud run services describe $ServiceName `
    --project=$ProjectId `
    --region=$Region `
    --format="value(status.url)"

if (-not $ServiceUrl) {
    throw "Cloud Run service URL could not be resolved. Deploy ORPHEUS first."
}

$TargetUrl = "$ServiceUrl/autonomy/cycle"
$ExistingJob = gcloud scheduler jobs describe $JobName `
    --project=$ProjectId `
    --location=$SchedulerRegion `
    --format="value(name)" 2>$null

if ($ExistingJob) {
    gcloud scheduler jobs update http $JobName `
        --project=$ProjectId `
        --location=$SchedulerRegion `
        --schedule=$Schedule `
        --time-zone=$TimeZone `
        --uri=$TargetUrl `
        --http-method=POST `
        --oidc-service-account-email=$ServiceAccount `
        --oidc-token-audience=$ServiceUrl | Out-Null
} else {
    gcloud scheduler jobs create http $JobName `
        --project=$ProjectId `
        --location=$SchedulerRegion `
        --schedule=$Schedule `
        --time-zone=$TimeZone `
        --uri=$TargetUrl `
        --http-method=POST `
        --oidc-service-account-email=$ServiceAccount `
        --oidc-token-audience=$ServiceUrl | Out-Null
}

Write-Host "Autonomous scheduler configured."
Write-Host "Job: $JobName"
Write-Host "Schedule: $Schedule ($TimeZone)"
Write-Host "Target: $TargetUrl"
Write-Host "Run a test with: gcloud scheduler jobs run $JobName --location=$SchedulerRegion --project=$ProjectId"
