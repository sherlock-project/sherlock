#define MyAppName "Beyond The Naked Eye"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Beyond The Naked Eye Labs"
#define MyAppURL "https://example.com/beyond-the-naked-eye"
#define MyAppExeName "BeyondTheNakedEye.exe"

[Setup]
AppId={0B95BDF8-36AF-4D03-B5D0-9C3CC5EAA19E}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=Beyond The Naked Eye Intelligence Workstation Installer
DefaultDirName={autopf}\Beyond The Naked Eye
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\..\LICENSE
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
OutputBaseFilename=BeyondTheNakedEye_Setup
SetupLogging=yes
Compression=lzma2
SolidCompression=yes
UninstallDisplayIcon={app}\{#MyAppExeName}
CreateUninstallRegKey=yes
Uninstallable=yes
UsePreviousAppDir=no
DisableProgramGroupPage=no

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "quicklaunchicon"; Description: "Create a Quick Launch shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Dirs]
Name: "{app}\modules"
Name: "{app}\themes"
Name: "{app}\assets"
Name: "{app}\cache"
Name: "{app}\database"
Name: "{app}\logs"
Name: "{app}\exports"
Name: "{app}\sessions"
Name: "{app}\plugins"
Name: "{userappdata}\BeyondTheNakedEye\configs"
Name: "{userappdata}\BeyondTheNakedEye\sessions"
Name: "{userappdata}\BeyondTheNakedEye\cache"
Name: "{userappdata}\BeyondTheNakedEye\settings"
Name: "{userappdata}\BeyondTheNakedEye\history"
Name: "{userappdata}\BeyondTheNakedEye\logs"

[Files]
Source: "..\..\dist\BeyondTheNakedEye\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "{cmd}"; Parameters: "/C if exist \"{app}\\logs\" rmdir /S /Q \"{app}\\logs\""; Flags: runhidden

[Code]
var
  DiagnosticsPage: TOutputProgressWizardPage;

procedure InitializeWizard;
begin
  WizardForm.Color := clBlack;
  WizardForm.Font.Color := clWhite;
  WizardForm.WelcomeLabel1.Font.Color := clWhite;
  WizardForm.WelcomeLabel2.Font.Color := clGray;

  DiagnosticsPage := CreateOutputProgressPage(
    'Installation Diagnostics',
    'Initializing monochrome tactical workstation modules...'
  );
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    DiagnosticsPage.Show;
    DiagnosticsPage.SetText('Installing core modules', 'Verifying runtime packages and terminal rendering support');
    DiagnosticsPage.SetProgress(1, 6);
    DiagnosticsPage.Add('Initializing configuration directories...');
    DiagnosticsPage.SetProgress(2, 6);
    DiagnosticsPage.Add('Preparing cache and log pipelines...');
    DiagnosticsPage.SetProgress(3, 6);
    DiagnosticsPage.Add('Mounting archive and export directories...');
    DiagnosticsPage.SetProgress(4, 6);
    DiagnosticsPage.Add('Validating CRT theme assets...');
    DiagnosticsPage.SetProgress(5, 6);
    DiagnosticsPage.Add('Finalizing workstation bootstrap...');
    DiagnosticsPage.SetProgress(6, 6);
    DiagnosticsPage.Hide;
  end;
end;
