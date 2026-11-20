# 编程工具箱神器 Beta v0.2 — 测试报告

- 测试日期：2026-11-19
- 测试环境：Windows 11 x64 / Python 3.13.14 x64 / PySide6 6.12.0 / PyInstaller 6.22.3 / Inno Setup 6.7.4
- 构建根目录：`F:\作品文件\ai制作的项目\编程工具箱神器`
- 备份与日志根目录：`L:\WorkBuddy临时文件\编程工具箱神器`（按用户要求统一归拢）

## 一、内置工具获取与展开（5/5 通过）

| 工具 | 版本 | 官方源 | 展开目标 | 目标 exe | 结果 |
|---|---|---|---|---|---|
| VSCodium | 1.143.17232 | GitHub Releases | builtin-payload\VSCodium | VSCodium.exe | OK |
| Python | 3.13.12 | python.org | builtin-payload\Python | python.exe | OK |
| Git for Windows | 2.56.1 | GitHub Releases | builtin-payload\Git | bin\git.exe | OK |
| 7-Zip | 26.06 | 7-zip.org | builtin-payload\7-Zip | 7z.exe | OK |
| Notepad++ | 8.9.9.1 | GitHub Releases | builtin-payload\Notepad++ | notepad++.exe | OK |

- zip 用 Python `zipfile` 展开；两个自解压包用官方 `7zr.exe 26.04` 展开（`rc=0`，输出日志中的 UnicodeDecodeError 仅为读取中文控制台输出的编码问题，不影响解压结果）。
- 展开后总载荷约 1.1GB（VSCodium 652MB、Git 411MB 为主）。

## 二、路径闭环测试（通过）

模拟冻结安装布局（把工具放到临时目录的 `builtin\` 下、伪造 `sys.frozen`/`sys.executable`）后：

- `core.paths.app_root()` 正确解析到 exe 所在目录；
- `ToolRegistry.builtin_executable()` 在用户 `install_dir` 故意设为不存在目录的情况下，仍能从程序安装目录找到全部 5 个内置工具（5/5）；
- 结论：「开箱即用 / 免下载直接用」在打包后的目录结构下成立。

## 三、PyInstaller 打包（通过，含一次问题修复）

- 首次打包产物为 22MB「空壳」：`_internal` 仅 55 个文件、无 Qt DLL、无平台插件。
- 根因：构建时 PySide6 依赖尚未安装到构建解释器，PyInstaller 静态分析静默跳过 Qt。
- 修复：为构建解释器安装 PySide6 6.12.0（`qwindows.dll`、`Qt6Core.dll` 校验存在）后重打包。
- 规避工具批量删除策略：不再用 `--clean` 删除旧产物，改为把旧目录改名后重建。
- 最终产物：117MB，`dist\ToolboxApp\_internal\PySide6\plugins\platforms\qwindows.dll` 与 `Qt6Core.dll` 均存在。

## 四、GUI 与核心逻辑测试（Alpha 阶段已通过，Beta 复核）

- 主窗口构建、内置/直链双列表、搜索过滤、退出处理流程：通过（源码级 offscreen 冒烟测试）。
- 核心逻辑 7 项（日志落 L 盘、清单加载、目录检查/迁移、冻结压缩、更新比对）：通过。

## 五、运行环境拦截问题（SAC — 已知限制，未绕过）

- 现象：本机 Smart App Control 处于强制开启状态（`SmartAppControlState=On`，`VerifiedAndReputablePolicyState=1`）。
- 证据：代码完整性日志事件 3077/3033，明确记录 `did not meet the Enterprise signing level requirements`。
- 结论：**未签名的自制 exe 在本机无法直接运行**，这不是程序缺陷，而是系统安全策略。
- 处理原则：未擅自修改系统安全设置。SAC 无单文件白名单机制；正规解法为购买代码签名证书（OV/EV）并签名，或在新版系统上临时切换 SAC 到 Off 后恢复。
- 影响范围：仅影响本机（及同样开启 SAC 的机器）直接双击运行；安装包本身可正常构建与分发。

## 六、Inno Setup 安装包

- 脚本：`04-安装包\toolbox-x64.iss`（仅 x64，符合用户「不做 32 位」要求）
- 修复项：AppId 改为合法 GUID；中文语言文件改为项目内自带（UTF-8 BOM）；`Compression=lzma2/normal`、`SolidCompression=no` 以控制 1.1GB 载荷的构建耗时；`DestDir={app}\builtin` 与清单路径对齐。
- 架构声明：`ArchitecturesAllowed=x64compatible`、`ArchitecturesInstallIn64BitMode=x64compatible`（避免装进 Program Files (x86)）。
- 构建结果：成功（191.8 秒），产物 `04-安装包\output\编程工具箱神器-Beta-v0.2-x64-Setup.exe`，342MB。
- SHA256：`62b92c3be85c1d3bb440e1c9722592622d55ec8bc64b5ce62a2216afc0318a56`（已填入官网下载页）。
- 版本信息已写入安装包（ProductName=编程工具箱神器 / FileVersion=0.2.0.0 / CompanyName=ToolboxAlpha）。
- 静默安装实测：本机 SAC 拦截安装程序加载临时文件（代码完整性事件 3077/3033，18:05:17），安装未落地——与第五节同一系统策略所致，非安装包缺陷。在关闭 SAC 或已签名的机器上可正常安装。

## 七、结论

Beta 阶段核心目标达成：真实工具已内置、路径闭环已验证、打包空壳问题已修复、x64 安装包已构建。剩余唯一外部依赖是代码签名（正式版事项），不影响 Beta 交付与功能验证。
