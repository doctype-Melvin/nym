[Setup]
AppName=Complyable
AppId={{5E8D5D40-03F5-4BA2-A97E-259384350232}}
AppVersion=0.1.0
DefaultDirName={commonappdata}\Complyable
DefaultGroupName=Complyable
PrivilegesRequired=admin
OutputDir=Output
OutputBaseFilename=Complyable-Setup
SetupIconFile=.\assets\COMPLYABLE.ico
UninstallDisplayName=Complyable
AlwaysShowDirOnReadyPage=yes

[Files]
Source: ".\installer\phase1-wsl2.ps1"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\installer\phase2-container.ps1"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\installer\phase3-launch.ps1"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\installer\docker-compose.yml"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion

[Run]
Filename: "{cmd}"; \
    Parameters: "/c %SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""{commonappdata}\Complyable\phase1-wsl2.ps1"""; \
    WorkingDir: "{commonappdata}\Complyable"; \
    Flags: runascurrentuser waituntilterminated; \
    StatusMsg: "Initializing WSL2 and System Requirements (This may take a minute)..."