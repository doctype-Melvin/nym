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

[Icons]
Name: "{commondesktop}\Start Complyable"; Filename: "{commonappdata}\Complyable\launcher.bat"; IconFilename: "{app}\complyable_start.ico"
Name: "{commondesktop}\Shutdown Complyable"; Filename: "powershell.exe"; Parameters: "-Command ""podman machine stop"""; IconFilename: "{app}\complyable_stop.ico"

[Files]
Source: ".\installer\install-complyable.ps1"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\installer\launcher.bat"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion

[Run]
Filename: "{commonappdata}\Complyable\launcher.bat"; \
    Flags: runascurrentuser waituntilterminated; \
    StatusMsg: "Initializing System..."