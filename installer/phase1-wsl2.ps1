# 1. Setup Environment
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Write-Step($msg) { Write-Host ""; Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red; exit 1 }

# 2. Windows Version Check
Write-Step "Checking Windows version..."
$build = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").CurrentBuildNumber
$build = [int]$build
if ($build -lt 19041) {
    Write-Fail "Complyable requires Windows 10 2004 (build 19041) or later. Current build: $build"
}
Write-Success "Windows build $build OK"

# 3. WSL2 & Virtual Machine Platform Check
Write-Step "Checking WSL2 status..."
$wsl = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
$vm  = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

if ($wsl.State -ne "Enabled" -or $vm.State -ne "Enabled") {
    Write-Host "Enabling WSL2 features — a restart will be required." -ForegroundColor Yellow
    
    # Enable features without immediate restart
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart | Out-Null
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart | Out-Null

    # 4. Prepare for Reboot & Resume
    $flagDir = "$env:ProgramData\Complyable"
    if (!(Test-Path $flagDir)) { New-Item -ItemType Directory -Force -Path $flagDir | Out-Null }
    "phase2" | Set-Content -Path "$flagDir\install_phase.txt" -Force

    # 5. Schedule Phase 2 to run at next Login
    $phase2Script = Join-Path $flagDir "phase2-container.ps1"
    $taskName = "Complyable-Phase2"
    
    # The 'NoExit' flag is vital so the user can see the progress/errors in Phase 2
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-NoProfile -ExecutionPolicy Bypass -NoExit -File `"$phase2Script`""
    
    # GroupId 'Users' ensures the window pops up on the interactive desktop
    $principal = New-ScheduledTaskPrincipal -GroupId "Users" -RunLevel Highest
    $trigger = New-ScheduledTaskTrigger -AtLogOn

    # Clean up old tasks and register new one
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null

    Write-Host "`n[ACTION REQUIRED] WSL2 enabled. Restarting in 10 seconds..." -ForegroundColor Yellow
    Write-Host "The installation will resume automatically after you log back in." -ForegroundColor Cyan
    
    Start-Sleep -Seconds 10
    Restart-Computer -Force
    exit 0
}

# 6. Final State: Already Enabled
Write-Success "WSL2 already enabled"
Write-Host "`nPhase 1 complete. Starting Phase 2 immediately..." -ForegroundColor Green

# If already enabled, just chain directly into Phase 2 without a reboot
& "$env:ProgramData\Complyable\phase2-container.ps1"