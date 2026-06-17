#define MyAppName "GAMAN Auditoria de Caja Fuerte"
#define MyAppVersion "7.0"
#define MyAppPublisher "Santiago Agudelo - GAMAN"
#define MyAppExeName "GAMAN_Auditoria_Caja_Fuerte.exe"

[Setup]
AppId={{4E69D6B4-2CC5-4C78-B430-7A0A4CF50731}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\GAMAN\AuditoriaCajaFuerte
DefaultGroupName=GAMAN
DisableProgramGroupPage=yes
OutputDir=Output
OutputBaseFilename=Instalador_GAMAN_Auditoria_Caja_Fuerte_V7
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: checkedonce

[Files]
Source: "dist\GAMAN_Auditoria_Caja_Fuerte\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\Resultados"

[Icons]
Name: "{group}\GAMAN Auditoria de Caja Fuerte"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\GAMAN Auditoria de Caja Fuerte"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir GAMAN Auditoria de Caja Fuerte"; Flags: nowait postinstall skipifsilent
