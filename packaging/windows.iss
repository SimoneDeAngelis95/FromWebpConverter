#ifndef AppVersion
  #error AppVersion must be supplied by the build
#endif
[Setup]
AppId={{39A4C84B-7594-4DB4-8B10-F35DB9F888EF}
AppName=From Webp Converter
AppVersion={#AppVersion}
AppPublisher=Simone De Angelis
DefaultDirName={localappdata}\Programs\FromWebpConverter
DefaultGroupName=From Webp Converter
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist\installer
OutputBaseFilename=FromWebpConverter-{#AppVersion}-windows-x64-Setup
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\FromWebpConverter.exe
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
[Files]
Source: "..\dist\FromWebpConverter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\From Webp Converter"; Filename: "{app}\FromWebpConverter.exe"
[Run]
Filename: "{app}\FromWebpConverter.exe"; Description: "Launch From Webp Converter"; Flags: nowait postinstall skipifsilent
