# Complyable Pilot Deployment Script
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

$IMAGE = "ghcr.io/doctype-melvin/complyable:latest"
$CONTAINER_NAME = "complyable-app"
$PODMAN_PATH = "C:\Program Files\RedHat\Podman"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# 1. Initialize Podman Machine
Write-Step "Initializing Podman Environment..."
$status = podman machine list
if ($status -notmatch "podman-machine-default") {
    podman machine init --disk-size 20 --memory 4096 --rootful
}

# 2. Start Machine and Handle Proxy Bug
Write-Step "Starting Machine & Network Bridge..."
podman machine start

# WATCHDOG: Force gvproxy if it failed to start
$proxy = Get-Process gvproxy -ErrorAction SilentlyContinue
if (-not $proxy) {
    Write-Host "Manual Watchdog: Starting gvproxy.exe..." -ForegroundColor Yellow
    Start-Process "$PODMAN_PATH\gvproxy.exe" -ArgumentList "-ssh-port 2222 -listen-no-zap" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

# 3. Setup Named Volumes (Solves 'statfs' and Permission Errors)
Write-Step "Preparing Data Volumes..."
podman volume create complyable_vault
podman volume create complyable_output
podman volume create complyable_input

# 4. Launch Container
Write-Step "Launching Complyable (Clean State)..."
podman rm -f $CONTAINER_NAME 2>$null

podman run -d `
  --name $CONTAINER_NAME `
  --restart unless-stopped `
  -p 8501:8501 `
  -e "STREAMLIT_SERVER_HEADLESS=true" `
  -e "STREAMLIT_SERVER_ADDRESS=0.0.0.0" `
  -v "complyable_vault:/app/data/vault" `
  -v "complyable_output:/app/data/output" `
  -v "complyable_input:/app/data/input" `
  $IMAGE

# 5. Final Connection Check
Write-Host "`nWaiting for Streamlit to warm up..." -ForegroundColor Yellow
for ($i=15; $i -gt 0; $i--) { Write-Host "$i... " -NoNewline; Start-Sleep 1 }

Write-Step "Opening Complyable..."
Start-Process "http://127.0.0.1:8501"

Write-Host "`n============================================" -ForegroundColor Green
Write-Host " SUCCESS: Complyable is deployed." -ForegroundColor Green
Write-Host "============================================`n"