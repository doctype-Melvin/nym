# --- 0. SELF-ELEVATION (Fixes Error 740) ---
if (!([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "Requesting Administrator privileges..." -ForegroundColor Yellow
    Start-Process powershell.exe "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# --- 1. GLOBAL CONFIGURATION ---
$IMAGE = "ghcr.io/doctype-melvin/complyable:linux-amd64"
$CONTAINER_NAME = "complyable-app"
$PODMAN_PATH = "C:\Program Files\RedHat\Podman"
$LAUNCHER = "$env:ProgramData\Complyable\launcher.bat"
$FLAG_FILE = "$env:ProgramData\Complyable\installed.flag"
$WSL_EXE = "$env:SystemRoot\System32\wsl.exe"

# Force modern TLS and Path Refresh for the session
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# --- 2. THE FAST-TRACK (For subsequent launches) ---
if (Test-Path $FLAG_FILE) {
    Write-Host "Complyable is already installed. Waking up services..." -ForegroundColor Green
    
    # Check if Podman is running
    $status = & "$PODMAN_PATH\podman.exe" machine inspect --format "{{.State}}" 2>$null
    if ($status -ne "running") {
        & "$PODMAN_PATH\podman.exe" machine start
    }
    
    # Ensure gvproxy is alive
    if (!(Get-Process gvproxy -ErrorAction SilentlyContinue)) {
        Start-Process "$PODMAN_PATH\gvproxy.exe" -ArgumentList "-ssh-port 2222 -listen-no-zap" -WindowStyle Hidden
    }
    
    & "$PODMAN_PATH\podman.exe" start $CONTAINER_NAME 2>$null
    Start-Process "http://complyable.local:8501"
    Start-Sleep -Seconds 3
    Stop-Process -Id $PID
    exit
}

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }

# --- 3. PHASE 0: Pre-Flight (WSL & Virtualization) ---
Write-Step "Checking System Requirements..."
$wslFeat = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
$vmFeat = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

if ($wslFeat.State -ne "Enabled" -or $vmFeat.State -ne "Enabled") {
    Write-Host "Enabling WSL and Virtualization Platform..." -ForegroundColor Yellow
    dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart /quiet
    dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart /quiet
    
    # Set the Resume key so it continues after reboot
    Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\RunOnce" -Name "ResumeComplyable" -Value "$LAUNCHER"
    
    Write-Host "`n[REBOOT REQUIRED] System features enabled." -ForegroundColor Red
    Write-Host "Press any key to REBOOT NOW..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    Restart-Computer
    exit
}

# --- 4. PHASE 1: Podman Installation (Winget) ---
if (!(Get-Command podman -ErrorAction SilentlyContinue)) {
    Write-Step "Installing Podman via Winget..."
    winget install -e --id RedHat.Podman --silent --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# --- 5. PHASE 2: Podman Init (Ghost Buster Logic) ---
Write-Step "Initializing Podman Environment..."
$initResult = & "$PODMAN_PATH\podman.exe" machine init --disk-size 20 --memory 4096 --rootful 2>&1
if ($initResult -match "already exists") {
    Write-Host "Detected Ghost VM. Force-cleaning WSL Registration..." -ForegroundColor Yellow
    & $WSL_EXE --unregister podman-machine-default
    & "$PODMAN_PATH\podman.exe" machine init --disk-size 20 --memory 4096 --rootful
}

# --- 6. PHASE 3: Networking & Services ---
Write-Step "Starting Machine & Network Bridge..."
& "$PODMAN_PATH\podman.exe" machine start

if (!(Get-Process gvproxy -ErrorAction SilentlyContinue)) {
    Start-Process "$PODMAN_PATH\gvproxy.exe" -ArgumentList "-ssh-port 2222 -listen-no-zap" -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

# --- 7. PHASE 4: Container Launch & Mirroring ---
Write-Step "Launching Complyable App..."
$BASE_DIR = "C:\Complyable"
$VAULT = "$BASE_DIR\Vault"
$OUTPUT = "$BASE_DIR\Output"
New-Item -ItemType Directory -Force -Path $VAULT, $OUTPUT | Out-Null

# Clear port conflicts
netsh interface portproxy reset

# Final Run
& "$PODMAN_PATH\podman.exe" run -d `
  --name $CONTAINER_NAME `
  --restart unless-stopped `
  -p 8501:8501 `
  -v "$($VAULT):/app/data/vault:Z" `
  -v "$($OUTPUT):/app/data/output:Z" `
  $IMAGE

# --- 8. PHASE 5: Custom URL & Finalizing ---
$hostsPath = "$env:SystemRoot\System32\drivers\etc\hosts"
if (!(Select-String -Path $hostsPath -Pattern "complyable.local")) {
    Add-Content -Path $hostsPath -Value "`n127.0.0.1    complyable.local" -ErrorAction SilentlyContinue
}

New-Item -Path $FLAG_FILE -ItemType File -Force | Out-Null
Start-Process "http://complyable.local:8501"

Write-Host "`nSUCCESS: Complyable is deployed." -ForegroundColor Green
Write-Host "Closing in 3 seconds..."
Start-Sleep -Seconds 3
Stop-Process -Id $PID