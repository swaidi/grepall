; GrepAll - Windows installer (Inno Setup 6)
; Copyright (C) 2026 A.T.Grep
; Licensed under the GNU Affero General Public License v3.0. See LICENSE.
;
; Built automatically by "build_exe.py --package" on Windows when Inno Setup is available.
; The build script passes: AppVersion, SourceDir (the dist\GrepAll folder), DocsDir, IconFile, OutputDir.
; Installs for the current user only, so no administrator rights are needed.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6B0E2C41-8F57-4C8D-9A0B-3E5D7A2F1C64}
AppName=GrepAll
AppVersion={#AppVersion}
AppVerName=GrepAll {#AppVersion}
AppPublisher=A.T.Grep
AppPublisherURL=https://github.com/swaidi/grepall
AppSupportURL=https://github.com/swaidi/grepall/issues
AppUpdatesURL=https://github.com/swaidi/grepall/releases
AppComments=Offline OCR for PDFs and images, with Arabic support
VersionInfoVersion={#AppVersion}
PrivilegesRequired=lowest
DefaultDirName={autopf}\GrepAll
DefaultGroupName=GrepAll
DisableProgramGroupPage=yes
DisableDirPage=auto
OutputDir={#OutputDir}
OutputBaseFilename=GrepAll-v{#AppVersion}-Windows-Setup
SetupIconFile={#IconFile}
UninstallDisplayIcon={app}\GrepAll.exe
UninstallDisplayName=GrepAll
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[InstallDelete]
; Remove the previous version's components first, so no outdated files remain after an update.
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#DocsDir}\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#DocsDir}\THIRD_PARTY_NOTICES.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#DocsDir}\READ_ME_FIRST.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\GrepAll"; Filename: "{app}\GrepAll.exe"; Comment: "Offline OCR for PDFs and images"
Name: "{group}\Read me first"; Filename: "{app}\READ_ME_FIRST.txt"
Name: "{group}\Uninstall GrepAll"; Filename: "{uninstallexe}"
Name: "{autodesktop}\GrepAll"; Filename: "{app}\GrepAll.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\GrepAll.exe"; Description: "Start GrepAll now"; Flags: nowait postinstall skipifsilent
