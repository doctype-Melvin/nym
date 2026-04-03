# Complyable Pilot Deployment Script - "Bare Metal" Edition
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

$IMAGE = "ghcr.io/doctype-melvin/complyable:linux-amd64"
$CONTAINER_NAME = "complyable-app"
$PODMAN_PATH = "C:\Program Files\RedHat\Podman"
$LAUNCHER = "$env:ProgramData\Complyable\launcher.bat"

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# --- PHASE 0: Pre-Flight Checks (Podman & WSL) ---
Write-Step "Checking System Requirements..."

# 1. Check WSL Feature
$wslFeature = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
if ($wslFeature.State -ne "Enabled") {
    Write-Host "==> WSL Feature is missing. Enabling now..." -ForegroundColor Yellow
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux, VirtualMachinePlatform -NoRestart
    
    # Set Resume Key for Reboot
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce" -Name "ResumeComplyable" -Value "$LAUNCHER"
    
    Write-Host "`n[REBOOT REQUIRED] Windows features enabled." -ForegroundColor Red
    Write-Host "Installation will resume automatically after login."
    Write-Host "Press any key to REBOOT NOW..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Restart-Computer
    exit
}

# 2. Check Podman Binary
if (!(Get-Command podman -ErrorAction SilentlyContinue)) {
    Write-Host "==> Podman not found. Installing..." -ForegroundColor Yellow
    $msiPath = "$env:TEMP\podman.msi"
    Invoke-WebRequest -Uri "https://github.com/containers/podman/releases/download/v5.0.1/podman-v5.0.1.msi" -OutFile $msiPath
    Start-Process msiexec.exe -ArgumentList "/i `"$msiPath`" /quiet /qn /norestart" -Wait
    # Refresh Path for current session
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# --- PHASE 1: Initialize Podman Machine ---
Write-Step "Initializing Podman Environment..."
try {
    $status = podman machine list
    if ($status -notmatch "podman-machine-default") {
        podman machine init --disk-size 20 --memory 4096 --rootful
    }
} catch {
    Write-Host "First-time init starting..."
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