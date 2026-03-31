# Complyable Installer Script
# Run as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator!"
    Break
}
$ErrorActionPreference = "Stop"
$AppName = "Complyable"
$ContainerName = "complyable-app"
$ImageName = "ghcr.io/doctype-melvin/complyable:latest"
$AppPort = 8501
$GHCRToken = "CUSTOMER_TOKEN_PLACEHOLDER"
$GHCRUser = "doctype-melvin"

function Write-Step($msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

function Write-Success($msg) {
    Write-Host "$msg" -ForegroundColor Green
}

function Write-Fail($msg) {
    Write-Host "$msg" -ForegroundColor Red
}

# ── Step 1: Check Windows version ─────────────────────────────────────────────
# Write-Step "Checking Windows version..."
# $winVersion = [System.Environment]::OSVersion.Version
# if ($winVersion.Major -lt 10 -or ($winVersion.Major -eq 10 -and $winVersion.Build -lt 19041)) {
#     Write-Fail "Complyable requires Windows 10 version 2004 or later."
#     exit 1
# }
# Write-Success "Windows version OK ($($winVersion.Build))"

# ── Step 2: Check/Enable WSL2 ─────────────────────────────────────────────────
Write-Step "Checking WSL2..."
$wslStatus = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
$vmStatus = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

if ($wslStatus.State -ne "Enabled" -or $vmStatus.State -ne "Enabled") {
    Write-Host "WSL2 needs to be enabled. This requires a restart." -ForegroundColor Yellow
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart
    
    # Save restart flag so installer continues after reboot
    $restartFlag = "$env:TEMP\complyable_resume.flag"
    Set-Content $restartFlag "resume"
    
    # Schedule task to resume after reboot
    $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
        -Argument "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
    Register-ScheduledTask -TaskName "ComplyableInstallResume" `
        -Action $action -Trigger $trigger -Principal $principal -Force

    Write-Host "`nRestart required. The installation will continue automatically after restart." -ForegroundColor Yellow
    Read-Host "Press Enter to restart now"
    Restart-Computer -Force
    exit 0
}
Write-Success "WSL2 available"

# ── Step 3: Clean up resume task if present ───────────────────────────────────
$restartFlag = "$env:TEMP\complyable_resume.flag"
if (Test-Path $restartFlag) {
    Remove-Item $restartFlag
    Unregister-ScheduledTask -TaskName "ComplyableInstallResume" -Confirm:$false -ErrorAction SilentlyContinue
    Write-Success "Resumed after restart"
}

# ── Step 4: Check/Install Rancher Desktop ─────────────────────────────────────
Write-Step "Checking Rancher Desktop..."
$rancherInstalled = Get-Command "rdctl" -ErrorAction SilentlyContinue

if (-not $rancherInstalled) {
    Write-Host "Rancher Desktop not found. Downloading..." -ForegroundColor Yellow
    
    $rancherUrl = "https://github.com/rancher-sandbox/rancher-desktop/releases/latest/download/Rancher.Desktop.Setup.exe"
    $rancherInstaller = "$env:TEMP\RancherDesktop-Setup.exe"
    
    Write-Host "Downloading Rancher Desktop (this may take a few minutes)..."
    Invoke-WebRequest -Uri $rancherUrl -OutFile $rancherInstaller -UseBasicParsing
    
    Write-Host "Installing Rancher Desktop silently..."
    Start-Process -FilePath $rancherInstaller -ArgumentList "/S" -Wait
    
    # Wait for rdctl to become available
    $timeout = 120
    $elapsed = 0
    while (-not (Get-Command "rdctl" -ErrorAction SilentlyContinue) -and $elapsed -lt $timeout) {
        Start-Sleep -Seconds 5
        $elapsed += 5
        Write-Host "Waiting for Rancher Desktop to initialize... ($elapsed s)"
    }
    
    if (-not (Get-Command "rdctl" -ErrorAction SilentlyContinue)) {
        Write-Fail "Rancher Desktop installation failed or timed out."
        exit 1
    }
}
Write-Success "Rancher Desktop available"

# ── Step 5: Start Rancher Desktop engine ──────────────────────────────────────
Write-Step "Starting container engine..."
rdctl start --container-engine moby 2>$null
Start-Sleep -Seconds 10
Write-Success "Container engine ready"

# ── Step 6: Authenticate with GHCR ───────────────────────────────────────────
Write-Step "Authenticating with registry..."
$GHCRToken | docker login ghcr.io -u $GHCRUser --password-stdin
Write-Success "Authenticated"

# ── Step 7: Pull Complyable image ─────────────────────────────────────────────
Write-Step "Downloading Complyable (this will take several minutes)..."
docker pull $ImageName
Write-Success "Complyable downloaded"

# ── Step 8: Create data directory on host ────────────────────────────────────
Write-Step "Setting up data directory..."
$DataDir = "$env:USERPROFILE\Complyable\data"
New-Item -ItemType Directory -Force -Path "$DataDir\vault" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataDir\output" | Out-Null
New-Item -ItemType Directory -Force -Path "$DataDir\input" | Out-Null
Write-Success "Data directory: $DataDir"

# ── Step 9: Create launch script ──────────────────────────────────────────────
Write-Step "Creating launch script..."
$LaunchDir = "$env:USERPROFILE\Complyable"
$LaunchScript = "$LaunchDir\start-complyable.ps1"

$launchContent = @"
# Complyable Launch Script
`$ContainerName = "$ContainerName"
`$ImageName = "$ImageName"
`$DataDir = "`$env:USERPROFILE\Complyable\data"

# Remove existing container if stopped
`$existing = docker ps -a --filter "name=`$ContainerName" --format "{{.Names}}"
if (`$existing) {
    docker rm -f `$ContainerName | Out-Null
}

# Start container
docker run -d ``
    --name `$ContainerName ``
    -p 8501:8501 ``
    -v "`$DataDir\vault:/app/data/vault" ``
    -v "`$DataDir\output:/app/data/output" ``
    -v "`$DataDir\input:/app/data/input" ``
    `$ImageName

# Wait for app to be ready
Start-Sleep -Seconds 5
Start-Process "http://localhost:8501"
"@
Set-Content -Path $LaunchScript -Value $launchContent
Write-Success "Launch script created"

# ── Step 10: Create desktop shortcut ──────────────────────────────────────────
Write-Step "Creating desktop shortcut..."
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Complyable.lnk")
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$LaunchScript`""
$Shortcut.WorkingDirectory = $LaunchDir
$Shortcut.Description = "Start Complyable"
$Shortcut.Save()
Write-Success "Desktop shortcut created"

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Complyable installed successfully!" -ForegroundColor Green
Write-Host "  Use the desktop shortcut to launch." -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green