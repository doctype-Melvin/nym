# 1. Wait for System Stability
Write-Host "Waiting for system services..." -ForegroundColor Gray
Start-Sleep -Seconds 10 

# 2. Force Absolute Pathing
$baseDir = "C:\ProgramData\Complyable"
if (!(Test-Path $baseDir)) {
    # If the folder is missing, try to find where we are
    $baseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
Set-Location $baseDir

# 3. Logging (Create a log file so we can read it if it crashes)
$logFile = Join-Path $baseDir "install_log.txt"
"Phase 2 started at $(Get-Date)" | Out-File $logFile

# --- DEBUGGING HEADER ---
Write-Host "--- PHASE 2 STARTING ---" -ForegroundColor Yellow
$InfraDir = "C:\ProgramData\Complyable"

# FIX: Force the script to look in the right folder
if (Test-Path $InfraDir) { 
    Set-Location $InfraDir 
} else {
    Write-Host "ERROR: Installation directory $InfraDir not found!" -ForegroundColor Red
    Start-Sleep -Seconds 10
    exit 1
}

Write-Host "Current Location: $((Get-Location).Path)" -ForegroundColor Gray
Start-Sleep -Seconds 5  # Reduced to 5s for faster testing

# 1. CLEANUP: Stop the task from running again
Unregister-ScheduledTask -TaskName "Complyable-Phase2" -Confirm:$false -ErrorAction SilentlyContinue

# 2. VERIFY: Ensure we are in the right state
$flagPath = Join-Path $InfraDir "install_phase.txt"
if (!(Test-Path $flagPath) -or (Get-Content $flagPath) -ne "phase2") {
    Write-Host "Phase 2 flag not found. If you just rebooted, this is an error." -ForegroundColor Red
    Read-Host "Press Enter to exit..."
    exit 1
}

# 3. SETUP: Environment and Error Handling
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
$GHCR_TOKEN = "CUSTOMER_TOKEN_PLACEHOLDER"
$GHCR_USER  = "doctype-melvin"
$IMAGE      = "ghcr.io/doctype-melvin/complyable:latest"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red; Read-Host "Press Enter to exit..."; exit 1 }

trap {
    Write-Host "`nFATAL ERROR: $_" -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

# 4. EXECUTION: Podman Logic
Write-Step "Checking Podman Desktop..."

if (-not (Get-Command "podman" -ErrorAction SilentlyContinue)) {
    Write-Host "Podman not found. Installing via Winget..." -ForegroundColor Yellow
    
    # 1. Attempt install via Winget (Silent, force, and accept licenses)
    winget install --id RedHat.Podman-Desktop --silent --accept-package-agreements --accept-source-agreements --scope machine
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Winget failed or is missing. Trying alternative ID..." -ForegroundColor Gray
        winget install --id RedHat.Podman --silent --accept-package-agreements --accept-source-agreements
    }

    # 2. Refresh Path (Crucial: Winget installs to a new folder)
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}

Write-Success "Podman available"

# 1. Force the system to broadcast the PATH change
$env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

# 2. Check again. If it still fails, look in the default installation folder
if (-not (Get-Command "podman" -ErrorAction SilentlyContinue)) {
    Write-Host "Podman not in PATH yet. Checking default install directory..." -ForegroundColor Yellow
    $defaultPodmanPath = "C:\Program Files\RedHat\Podman"
    if (Test-Path $defaultPodmanPath) {
        $env:Path += ";$defaultPodmanPath"
        Write-Success "Manually added Podman to session PATH."
    } else {
        Write-Fail "Podman was installed but the executable could not be found."
    }
}

Write-Step "Initializing Podman machine..."
if ((podman machine list 2>&1) -notmatch "podman-machine-default") {
    podman machine init --disk-size 20 --memory 2048
}

if ((podman machine list 2>&1) -notmatch "Currently running") {
    podman machine start
}
Write-Success "Podman machine running"

Write-Step "Authenticating and Pulling Image..."
$GHCR_TOKEN | podman login ghcr.io -u $GHCR_USER --password-stdin
podman pull $IMAGE
Write-Success "Image ready"

# 5. TRANSITION: Phase 3
$phase3 = Join-Path $InfraDir "phase3-launch.ps1"
if (Test-Path $phase3) {
    Write-Host "`nLaunching UI..." -ForegroundColor Green
    & $phase3
}

Read-Host "`nInstallation Complete. Press Enter to finish..."