# 1. Environment & Variables (Define these FIRST)
$taskName = "Complyable-Phase2"
$flagDir = "$env:ProgramData\Complyable"
$phase2Script = "$flagDir\phase2-container.ps1"

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

function Write-Step($msg) { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }

# 2. Windows Version Check
Write-Step "Checking Windows version..."
$build = [int](Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").CurrentBuildNumber
Write-Success "Windows build $build OK"

# 3. WSL2 Feature Check
Write-Step "Checking WSL2 status..."
$wsl = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
$vm = Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform

if ($wsl.State -ne "Enabled" -or $vm.State -ne "Enabled") {
    Write-Host "Enabling WSL2 features... Admin rights required." -ForegroundColor Yellow
    
    # Enable features (This will fail if NOT Admin)
    Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart -ErrorAction Stop | Out-Null
    Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform -NoRestart -ErrorAction Stop | Out-Null

    # 4. Setup Flag
    if (!(Test-Path $flagDir)) { New-Item -ItemType Directory -Force -Path $flagDir | Out-Null }
    Set-Content -Path "$flagDir\install_phase.txt" -Value "phase2" -Force

    # 5. Schedule Phase 2 (Using SID for "Users" to avoid German/English name conflicts)
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -NoExit -File `"$phase2Script`""
    
    # S-1-5-32-545 is the universal ID for the 'Users' group globally
    $principal = New-ScheduledTaskPrincipal -GroupId "S-1-5-32-545" -RunLevel Highest
    $trigger = New-ScheduledTaskTrigger -AtLogOn

    # Remove old task if it exists
    if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    }

    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null

    Write-Host "Restarting in 10 seconds..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    Restart-Computer -Force
    exit 0
}

Write-Success "WSL2 OK. Starting Phase 2..."
& $phase2Script