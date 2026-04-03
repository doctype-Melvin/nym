[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

$IMAGE = "ghcr.io/doctype-melvin/complyable:linux-amd64"
$CONTAINER_NAME = "complyable-app"
$PODMAN_PATH = "C:\Program Files\RedHat\Podman"
$LAUNCHER = "$env:ProgramData\Complyable\launcher.bat"
$FLAG_FILE = "$env:ProgramData\Complyable\installed.flag"

# --- Bypass Checks if Installed ---
if (Test-Path $FLAG_FILE) {
    # 1. Force refresh the PATH so the script can see "podman"
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

    Write-Host "Complyable is already installed. Starting services..." -ForegroundColor Green
    
    # 2. Define the absolute path to Podman to avoid "CommandNotFound"
    $PODMAN_EXE = "$PODMAN_PATH\podman.exe"

    # Ensure Podman is actually running
    # We use & to execute the string path
    $machineStatus = & $PODMAN_EXE machine inspect --format "{{.State}}" 2>$null
    
    if ($machineStatus -ne "running") {
        Write-Host "Waking up Podman..." -ForegroundColor Cyan
        & $PODMAN_EXE machine start
    }
    
    # Start gvproxy watchdog
    $proxy = Get-Process gvproxy -ErrorAction SilentlyContinue
    if (-not $proxy) {
        Write-Host "Starting Network Bridge..." -ForegroundColor Gray
        Start-Process "$PODMAN_PATH\gvproxy.exe" -ArgumentList "-ssh-port 2222 -listen-no-zap" -WindowStyle Hidden
    }
    
    # Ensure Container is running
    & $PODMAN_EXE start $CONTAINER_NAME 2>$null
    
    # Open Browser and Exit
    Start-Process "http://complyable.local:8501"
    Start-Sleep -Seconds 3
    Stop-Process -Id $PID
    exit
}

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# --- PHASE 0: Pre-Flight Checks (Podman & WSL) ---
Write-Step "Checking System Requirements..."

$wslPath = "$env:SystemRoot\System32\wsl.exe"
$feat = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

# Check if feature is missing OR if the wsl.exe binary is actually gone
if ($feat.State -ne "Enabled" -or !(Test-Path $wslPath)) {
    Write-Host "==> WSL or Virtualization Platform is not ready. Configuring..." -ForegroundColor Yellow
    
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
    
    # Set Resume Key
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce" -Name "ResumeComplyable" -Value "$LAUNCHER"
    
    Write-Host "`n[REBOOT REQUIRED] System features updated." -ForegroundColor Red
    Write-Host "Press any key to REBOOT NOW..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Restart-Computer
    exit
}

# 2. Check Podman Binary
if (!(Get-Command podman -ErrorAction SilentlyContinue)) {
    Write-Step "Podman not found. Installing via Winget..."
    
    # -e (Exact ID), --silent (No UI), --accept-source-agreements (Bypass prompts)
    winget install -e --id RedHat.Podman --silent --accept-source-agreements --accept-package-agreements
    
    # REFRESH PATH: Mandatory for the current session to see the new 'podman' command
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    if (!(Get-Command podman -ErrorAction SilentlyContinue)) {
        Write-Error "Winget installation failed to register 'podman'. Please restart the installer."
        exit 1
    }
}

# --- PHASE 1: Initialize Podman Machine ---
Write-Step "Initializing Podman Environment..."
$initTry = podman machine init --disk-size 20 --memory 4096 --rootful 2>&1
if ($initTry -match "already exists") {
    Write-Host "Ghost VM detected. Force-clearing Hypervisor..." -ForegroundColor Yellow
    & "$env:SystemRoot\System32\wsl.exe" --unregister podman-machine-default
    podman machine init --disk-size 20 --memory 4096 --rootful
}

# --- PHASE 2: Start Machine & Network Bridge ---
Write-Step "Starting Machine & Network Bridge..."
podman machine start

# WATCHDOG: Force gvproxy
$proxy = Get-Process gvproxy -ErrorAction SilentlyContinue
if (-not $proxy) {
    Write-Host "Manual Watchdog: Starting gvproxy.exe..." -ForegroundColor Yellow
    Start-Process "$PODMAN_PATH\gvproxy.exe" -ArgumentList "-ssh-port 2222 -listen-no-zap" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

# --- PHASE 3: Prepare Mirroring & Volumes ---
Write-Step "Preparing Data Mirroring..."
# Create local folders for the user to see
$BASE_DIR = "C:\Complyable"
$VAULT = "$BASE_DIR\Vault"
$OUTPUT = "$BASE_DIR\Output"
New-Item -ItemType Directory -Force -Path $VAULT, $OUTPUT | Out-Null

# --- PHASE 4: Launch Container ---
Write-Step "Launching Complyable..."
podman rm -f $CONTAINER_NAME 2>$null

Write-Step "Network & WSL Health Audit..."

# Clear any legacy portproxy rules that might conflict
netsh interface portproxy reset

# Show the actual WSL state to the user
$wslState = & "$env:SystemRoot\System32\wsl.exe" -l -v
Write-Host "WSL Engine Status:" -ForegroundColor Yellow
Write-Host $wslState

# Check if Virtualization is enabled (The most common "Bare Metal" fail point)
$feat = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -ErrorAction SilentlyContinue
Write-Host "Virtualization Platform: $($feat.State)" -ForegroundColor Gray

# Using Host-to-Container Mapping for Visibility
podman run -d `
  --name $CONTAINER_NAME `
  --restart unless-stopped `
  -p 8501:8501 `
  -e "STREAMLIT_SERVER_HEADLESS=true" `
  -v "$($VAULT):/app/data/vault:Z" `
  -v "$($OUTPUT):/app/data/output:Z" `
  $IMAGE

# --- PHASE 5: Custom URL Setup (Hosts File) ---
$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
$hostEntry = "127.0.0.1    complyable.local"
if (!(Select-String -Path $hostsPath -Pattern "complyable.local")) {
    Write-Step "Setting up custom URL: http://complyable.local:8501"
    Add-Content -Path $hostsPath -Value "`n$hostEntry" -ErrorAction SilentlyContinue
}

# --- PHASE 6: Finish ---
Write-Host "`nWaiting for app to stabilize..." -ForegroundColor Yellow
for ($i=10; $i -gt 0; $i--) { Write-Host "$i... " -NoNewline; Start-Sleep 1 }

Start-Process "http://complyable.local:8501"

Write-Host "`n============================================" -ForegroundColor Green
Write-Host " SUCCESS: Complyable is deployed at http://complyable.local:8501" -ForegroundColor Green
Write-Host " Files are mirrored at: $BASE_DIR" -ForegroundColor Green
Write-Host "============================================`n"

New-Item -Path $FLAG_FILE -ItemType File -Force | Out-Null
Write-Host "Installation Flag Created." -ForegroundColor Gray

Write-Host "Closing this window in 3 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# This forces the PowerShell process to kill itself and its parent window
Stop-Process -Id $PID