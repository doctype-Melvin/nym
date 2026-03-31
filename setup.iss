[Setup]
AppName=Complyable
AppVersion=0.1.0
DefaultDirName={autopf}\Complyable
DefaultGroupName=Complyable
PrivilegesRequired=admin
OutputDir=Output

[Files]
; Source is relative to the .iss file location in your repo
Source: "installer\install.ps1"; DestDir: "{app}"; Flags: ignoreversion
; Include any other necessary files here, e.g.:
; Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs

[Icons]
; This creates the shortcut to run the INSTALLATION script
Name: "{group}\Install Complyable"; Filename: "powershell.exe"; \
      Parameters: "-ExecutionPolicy Bypass -File ""{app}\install.ps1"""
Name: "{commondesktop}\Install Complyable"; Filename: "powershell.exe"; \
      Parameters: "-ExecutionPolicy Bypass -File ""{app}\install.ps1"""

[Run]
; Kicks off the script as soon as the Inno Setup wizard finishes
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\wrapper.ps1"""; Flags: postinstall nowait