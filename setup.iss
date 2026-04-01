[Setup]
AppName=Complyable
AppVersion=0.1.0
DefaultDirName={commonappdata}\Complyable
DefaultGroupName=Complyable
PrivilegesRequired=admin
OutputDir=Output
OutputBaseFilename=Complyable-Setup
SetupIconFile=.\assets\COMPLYABLE.ico
UninstallDisplayName=Complyable

[Files]
Source: ".\installer\phase1-wsl2.ps1"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\installer\phase2-container.ps1"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\installer\phase3-launch.ps1"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\installer\docker-compose.yml"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion

[Run]
Filename: "powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -File ""{commonappdata}\Complyable\phase1-wsl2.ps1"""; \
    WorkingDir: "{commonappdata}\Complyable"; \
    Flags: runascurrentuser waituntilterminated; \
    StatusMsg: "Setting up Complyable..."