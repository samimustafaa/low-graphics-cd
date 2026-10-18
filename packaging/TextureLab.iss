#define AppVersion "1.1.0"
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
[Icons]
Name: "{group}\Texture Lab"; Filename: "{app}\TextureLab.exe"
Name: "{autodesktop}\Texture Lab"; Filename: "{app}\TextureLab.exe"; Tasks: desktopicon
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
[Run]
Filename: "{app}\TextureLab.exe"; Description: "Open Texture Lab"; Flags: nowait postinstall skipifsilent
