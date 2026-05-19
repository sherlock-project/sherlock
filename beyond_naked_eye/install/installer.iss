[Setup]
AppName=Beyond The Naked Eye
AppVersion=1.0.0
DefaultDirName={autopf}\BeyondTheNakedEye
DefaultGroupName=Beyond The Naked Eye
OutputBaseFilename=BeyondTheNakedEye_Setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\BeyondTheNakedEye.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Beyond The Naked Eye"; Filename: "{app}\BeyondTheNakedEye.exe"
Name: "{autodesktop}\Beyond The Naked Eye"; Filename: "{app}\BeyondTheNakedEye.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create Desktop shortcut"; GroupDescription: "Additional icons:"
Name: "portablemode"; Description: "Enable portable mode"

[Run]
Filename: "{app}\BeyondTheNakedEye.exe"; Description: "Launch Beyond The Naked Eye"; Flags: nowait postinstall skipifsilent
