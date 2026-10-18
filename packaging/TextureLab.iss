#define AppVersion "1.6.2"
[Setup]
AppId={{5AF53953-9946-4A0A-BD65-2ED4641369B1}
AppName=Texture Lab
AppVersion={#AppVersion}
AppPublisher=sg0hann
AppPublisherURL=https://github.com/samimustafaa/low-graphics-cd
DefaultDirName={localappdata}\Programs\TextureLab
DefaultGroupName=Texture Lab
PrivilegesRequired=lowest
OutputDir=..\release
OutputBaseFilename=TextureLab-Setup-{#AppVersion}
SetupIconFile=..\app.ico
UninstallDisplayIcon={app}\TextureLab.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=..\LICENSE.txt
InfoBeforeFile=install_notes.txt
CloseApplications=yes
[Files]
Source: "..\dist\TextureLab.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "TextureLab-installed.txt"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\Texture Lab"; Filename: "{app}\TextureLab.exe"
Name: "{autodesktop}\Texture Lab"; Filename: "{app}\TextureLab.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
[Run]
Filename: "{app}\TextureLab.exe"; Description: "Open Texture Lab"; Flags: nowait postinstall skipifsilent; BeforeInstall: PrepareAppLaunch

Filename: "{app}\TextureLab.exe"; Flags: nowait; Check: IsUpdateInstall; BeforeInstall: PrepareAppLaunch
[Code]
function SetProcessEnvironment(Name, Value: String): Boolean;
  external 'SetEnvironmentVariableW@kernel32.dll stdcall';
function ResetDllSearch(Path: LongWord): Boolean;
  external 'SetDllDirectoryW@kernel32.dll stdcall';
procedure PrepareAppLaunch;
begin
  { Also repairs the handoff from older app versions whose updater inherited
    PyInstaller's temporary runtime. This affects this installer process only. }
  if not SetProcessEnvironment('PYINSTALLER_RESET_ENVIRONMENT', '1') then
    RaiseException('Could not prepare a fresh Texture Lab runtime. Reopen the app from its shortcut.');
  ResetDllSearch(0);
end;
function IsUpdateInstall: Boolean;
begin
  Result := ExpandConstant('{param:TEXTURELABUPDATE|0}') = '1';
end;
