# 1. Environment Setup
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
    Write-Fail "Windows build $build is too old. 19041+ required."
}
Write-Success "Windows build $build OK"

# 3. WSL2 Feature Check
Write-Step "Checking WSL2 and Virtual Machine Platform..."
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart -ErrorAction SilentlyContinue | Out-Null
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart -ErrorAction SilentlyContinue | Out-Null

if ($wsl.State -ne "Enabled" -or $vm.State -ne "Enabled") {
    Write-Host "Enabling WSL2 features... A restart will be required." -ForegroundColor Yellow
    
    # 3. Enable features
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart | Out-Null
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart | Out-Null

    # 4. Setup Reboot Persistence
    $flagDir = "$env:ProgramData\Complyable"
    if (!(Test-Path $flagDir)) { 
    New-Item -ItemType Directory -Force -Path $flagDir -ErrorAction SilentlyContinue | Out-Null 
    }
    Set-Content -Path "$flagDir\install_phase.txt" -Value "phase2" -Force

    # 5. Schedule Phase 2 (Note: No backticks here for maximum stability)
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    }
    $phase2Script = "$flagDir\phase2-container.ps1"
    $taskName = "Complyable-Phase2"
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -NoExit -File $phase2Script"
    $principal = New-ScheduledTaskPrincipal -GroupId "Users" -RunLevel Highest
    $trigger = New-ScheduledTaskTrigger -AtLogOn

    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null

    Write-Host "Restarting in 10 seconds. Installation resumes after login." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer -Force
    exit 0
}

# 6. Success / Chain to Phase 2
Write-Success "WSL2 is already enabled."
Write-Host "Proceeding to Phase 2 (Container Setup)..." -ForegroundColor Green

$phase2Path = "$env:ProgramData\Complyable\phase2-container.ps1"
if (Test-Path $phase2Path) {
    # Launching Phase 2 directly
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File $phase2Path
} else {
    Write-Host "ERROR: phase2-container.ps1 not found in $env:ProgramData\Complyable" -ForegroundColor Red
}