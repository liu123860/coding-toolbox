; ============================================================
; 编程工具箱神器 Beta v0.3 - Inno Setup 安装脚本（仅 x64）
; v0.3：内置工具 30 个；工具库 130 个；设置可调档位 30/50/60/80/100/130
; 编译：ISCC.exe toolbox-x64.iss
; 说明：脚本为 UTF-8 编码；中文语言文件为 UTF-8 BOM，放在项目内 Languages\
; ============================================================

#define MyAppName "编程工具箱神器"
#define MyAppVersion "0.3.0"
#define MyAppPublisher "ToolboxAlpha"
#define MyAppExeName "ToolboxApp.exe"

[Setup]
; ---- 基本信息（完整版本信息可降低杀软/SmartScreen 误报）----
; AppId 必须是合法 GUID（纯十六进制），否则编译报错
AppId={{A1B2C3D4-5E6F-4789-9A0B-1C2D3E4F5A6B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} Beta v0.3
AppPublisher={#MyAppPublisher}
VersionInfoVersion={#MyAppVersion}.0
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription=编程工具箱神器安装程序（开发人员的工具集与运行环境）
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCopyright=(C) 2026 ToolboxAlpha

; ---- 架构声明：仅 x64（关键！缺省会装进 Program Files (x86)）----
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

; ---- 安装目录 ----
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; 用户级安装，避免触发 UAC 提权（开箱即用）
PrivilegesRequired=lowest

; ---- 输出 ----
OutputDir=output
OutputBaseFilename=编程工具箱神器-Beta-v0.3-x64-Setup
; 内置 30 个工具（约 1.5GB 载荷），用较快的 normal 压缩档控制构建耗时
Compression=lzma2/normal
SolidCompression=no
WizardStyle=modern
SetupLogging=yes

; ---- 界面语言（项目内相对路径，零侵入，UTF-8 BOM）----
[Languages]
Name: "chinesesimplified"; MessagesFile: "Languages\ChineseSimplified.isl"

; ---- 安装内容 ----
; 注意：DestDir={app}\builtin 与 tools.json 中 builtin_path 前缀一致，
; 且与 core.paths.app_root()（exe 所在目录）解析出的路径对齐。
[Files]
; 主程序（PyInstaller onedir 产物：ToolboxApp.exe + _internal\）
Source: "..\02-程序源码\dist\ToolboxApp\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; 内置工具（已解压展开的真实目录结构，装完即可用）
Source: "..\03-资源文件\builtin-payload\*"; DestDir: "{app}\builtin"; Flags: ignoreversion recursesubdirs createallsubdirs

; ---- 快捷方式 ----
[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\卸载 {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "附加任务："; Flags: unchecked

; ---- 安装完成后可选启动 ----
[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "立即运行 {#MyAppName}"; Flags: nowait postinstall skipifsilent
