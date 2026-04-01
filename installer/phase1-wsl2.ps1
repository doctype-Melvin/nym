Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Write-Step($msg) { Write-Host ""; Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "[FAIL] $msg" -ForegroundColor Red; exit 1 }

Write-Step "Checking Windows version..."
$build = (Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").CurrentBuildNumber
$build = [int]$build
if ($build -lt 19041) {
    Write-Fail "Complyable requires Windows 10 2004 (build 19041) or later. Current build: $build"
}
Write-Success "Windows build $build OK"

Write-Step "Checking WSL2..."
$wsl = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
$vm  = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

if ($wsl.State -ne "Enabled" -or $vm.State -ne "Enabled") {
    Write-Host "Enabling WSL2 — a restart will be required." -ForegroundColor Yellow
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart | Out-Null
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart | Out-Null

    # Mark resume point
    $flag = "$env:ProgramData\Complyable\install_phase.txt"
    New-Item -ItemType Directory -Force -Path "$env:ProgramData\Complyable" | Out-Null
    Set-Content $flag "phase2"

    # Schedule phase2 to run after reboot
    $scriptPath = "$env:ProgramData\Complyable\phase2-container.ps1"
    $action = New-ScheduledTaskAction -Execute "powershell.exe" `
        -Argument "-ExecutionPolicy Bypass -NoExit -File `"$scriptPath`""
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest
    Register-ScheduledTask -TaskName "Complyable-Phase2" `
        -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null

    Write-Host "`nRestart required. Installation will continue automatically after restart." -ForegroundColor Yellow
    Read-Host "Press Enter to restart"
    Restart-Computer -Force
    exit 0
}

Write-Success "WSL2 already enabled"
Write-Host "`nPhase 1 complete. Proceeding to Phase 2..." -ForegroundColor Green