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
$podman = Get-Command "podman" -ErrorAction SilentlyContinue

if (-not $podman) {
Write-Host "Podman not found. Downloading Podman Desktop..." -ForegroundColor Yellow
    $podmanUrl = "https://github.com/containers/podman-desktop/releases/download/v1.14.1/podman-desktop-setup-1.14.1.exe"
    $podmanInstaller = "$env:TEMP\podman-desktop-setup.exe"

    # RETRY LOOP: Try 3 times to account for post-reboot network instability
    $maxRetries = 3
    $retryCount = 0
    $success = $false

    while (-not $success -and $retryCount -lt $maxRetries) {
        try {
            $retryCount++
            Write-Host "Download attempt $retryCount of $maxRetries..." -ForegroundColor Gray
            Invoke-WebRequest -Uri $podmanUrl -OutFile $podmanInstaller -UseBasicParsing -TimeoutSec 300
            $success = $true
        } catch {
            Write-Host "Download failed: $_" -ForegroundColor Red
            if ($retryCount -lt $maxRetries) {
                Write-Host "Waiting 10 seconds before retrying..." -ForegroundColor Yellow
                Start-Sleep -Seconds 10
            } else {
                Write-Fail "Could not download Podman after $maxRetries attempts. Please check your internet connection."
            }
        }
    }

    Write-Host "Installing silently..." -ForegroundColor Cyan
    Start-Process -FilePath $podmanInstaller -ArgumentList "/S" -Wait
    # Refresh Path
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
}
Write-Success "Podman available"

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