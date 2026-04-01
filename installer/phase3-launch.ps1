Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

$InfraDir   = "$env:ProgramData\Complyable"
$AppDataDir = "$env:LOCALAPPDATA\Complyable"
$IMAGE      = "ghcr.io/doctype-melvin/complyable:latest"

function Write-Step($msg) { Write-Host ""; Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }

Write-Step "Creating app data directories..."
New-Item -ItemType Directory -Force -Path "$AppDataDir\vault"  | Out-Null
New-Item -ItemType Directory -Force -Path "$AppDataDir\output" | Out-Null
New-Item -ItemType Directory -Force -Path "$AppDataDir\input"  | Out-Null
Write-Success "Data directories ready at $AppDataDir"

Write-Step "Writing docker-compose file..."
$composeContent = @"
version: "3.8"
services:
  complyable:
    image: $IMAGE
    container_name: complyable-app
    restart: unless-stopped
    ports:
      - "8501:8501"
    volumes:
      - $AppDataDir\vault:/app/data/vault
      - $AppDataDir\output:/app/data/output
      - $AppDataDir\input:/app/data/input
    environment:
      - DB_PATH=/app/data/vault/complyable_vault.db
      - CSV_PATH=/app/data/refs/dict_seed.csv
      - FONT_PATH=/usr/share/fonts/ArialUnicode.ttf
      - TORCH_CPP_LOG_LEVEL=ERROR
"@

Set-Content -Path "$InfraDir\docker-compose.yml" -Value $composeContent
Write-Success "Compose file written"

Write-Step "Starting Complyable for the first time..."
Set-Location $InfraDir
podman compose up -d
Start-Sleep -Seconds 8
Write-Success "Complyable started"

Write-Step "Creating desktop shortcut..."
$launchScript = "$InfraDir\launch.ps1"
$launchContent = @"
Set-Location "$InfraDir"
podman compose up -d
Start-Sleep -Seconds 5
Start-Process "http://localhost:8501"
"@
Set-Content -Path $launchScript -Value $launchContent

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$env:USERPROFILE\Desktop\Complyable.lnk")
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$launchScript`""
$shortcut.Description = "Launch Complyable"
$shortcut.Save()
Write-Success "Desktop shortcut created"

Start-Process "http://localhost:8501"

Write-Host "`n============================================" -ForegroundColor Green
Write-Host "  Complyable is ready!" -ForegroundColor Green
Write-Host "  Opening in your browser now." -ForegroundColor Green
Write-Host "  Use the desktop shortcut to launch it" -ForegroundColor Green
Write-Host "  again any time." -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Green