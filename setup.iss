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
Name: "{commondesktop}\Start Complyable"; Filename: "{commonappdata}\Complyable\launcher.bat"; IconFilename: "{app}\assets\COMPLYABLE.ico"
Name: "{commondesktop}\Shutdown Complyable"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -Command ""podman machine stop"""; IconFilename: "{app}\assets\shutdown.ico"

[Files]
Source: ".\installer\install-complyable.ps1"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\installer\launcher.bat"; DestDir: "{commonappdata}\Complyable"; Flags: ignoreversion
Source: ".\assets\COMPLYABLE.ico"; DestDir: "{app}\assets"; Flags: ignoreversion
Source: ".\assets\shutdown.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Run]
Filename: "{commonappdata}\Complyable\launcher.bat"; \
    Flags: runascurrentuser waituntilterminated; \
    StatusMsg: "Initializing System..."