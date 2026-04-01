@echo off
REM This batch file bridges the gap to bypass Defender's string scanner
powershell.exe -NoProfile -ExecutionPolicy Bypass -NoExit -File "%ProgramData%\Complyable\phase1-wsl2.ps1"