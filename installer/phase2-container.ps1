Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
trap {
    Write-Host "`nERROR: $_" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$GHCR_TOKEN = "CUSTOMER_TOKEN_PLACEHOLDER"
$GHCR_USER  = "doctype-melvin"
$IMAGE      = "ghcr.io/doctype-melvin/complyable:latest"
$InfraDir   = "$env:ProgramData\Complyable"

function Write-Step($msg) { Write-Host ""; Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red; exit 1 }

# Clean up resume task if this is a post-reboot run
Unregister-ScheduledTask -TaskName "Complyable-Phase2" -Confirm:$false -ErrorAction SilentlyContinue

Write-Step "Checking Podman Desktop..."
$podman = Get-Command "podman" -ErrorAction SilentlyContinue

if (-not $podman) {
    Write-Host "Podman not found. Downloading Podman Desktop..." -ForegroundColor Yellow

    $podmanUrl = "https://github.com/containers/podman-desktop/releases/latest/download/podman-desktop-setup.exe"
    $podmanInstaller = "$env:TEMP\podman-desktop-setup.exe"

    Write-Host "Downloading..."
    Invoke-WebRequest -Uri $podmanUrl -OutFile $podmanInstaller -UseBasicParsing

    Write-Host "Installing silently (this takes a few minutes)..."
    Start-Process -FilePath $podmanInstaller -ArgumentList "/S" -Wait

    # Refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + `
                [System.Environment]::GetEnvironmentVariable("Path", "User")

    $timeout = 120; $elapsed = 0
    while (-not (Get-Command "podman" -ErrorAction SilentlyContinue) -and $elapsed -lt $timeout) {
        Start-Sleep -Seconds 5; $elapsed += 5
        Write-Host "Waiting for Podman... ($elapsed s)"
    }

    if (-not (Get-Command "podman" -ErrorAction SilentlyContinue)) {
        Write-Fail "Podman installation failed or timed out."
    }
}
Write-Success "Podman available"

Write-Step "Initializing Podman machine..."
$machineList = podman machine list 2>&1
if ($machineList -notmatch "podman-machine-default") {
    podman machine init --disk-size 20 --memory 2048
}

$machineStatus = podman machine list 2>&1
if ($machineStatus -notmatch "Currently running") {
    podman machine start
}
Write-Success "Podman machine running"

Write-Step "Authenticating with registry..."
$GHCR_TOKEN | podman login ghcr.io -u $GHCR_USER --password-stdin
Write-Success "Authenticated"

Write-Step "Pulling Complyable image (this will take several minutes)..."
podman pull $IMAGE
Write-Success "Image downloaded"

Write-Host "`nPhase 2 complete. Proceeding to Phase 3..." -ForegroundColor Green

# Launch phase 3
$phase3 = "$InfraDir\phase3-launch.ps1"
if (Test-Path $phase3) {
    & $phase3
}