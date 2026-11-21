# 计算机人员专业工具箱（Coding Toolbox）

开箱即用、无账号、无广告、无收费的 Windows 开发者工具箱。常用工具内置即用，不常用工具按需下载，统一运行环境与目录管理。

- 版本：Beta v0.3
- 平台：Windows 10 / 11（仅 x64）
- 官网：https://v.gd/tHAYou
- 仓库：https://github.com/liu123860/coding-toolbox

## 功能特性

- **工具中心**：共 130 个工具，其中 30 个内置开箱即用，100 个可按需下载到指定目录；列表支持 Ctrl/Shift 多选，可批量启动、批量下载。
- **内置应用数量**：设置中可在 30 / 50 / 60 / 80 / 100 / 130 之间调整，工具库随数量扩展。
- **自带 Python 运行时**：内置 embeddable Python + PySide6，无需在目标电脑安装 Python 即可运行。
- **统一运行环境**：在工具箱内统一启动各类工具。
- **更新检查**：启动时从官方 JSON 清单检查新增 / 更新 / 下架工具，不爬取第三方网站。
- **退出冻结归档**：退出时询问是否压缩冻结用户数据、是否清理临时下载。
- **目录管理**：安装 / 下载 / 归档目录可自定义，修改时询问迁移，启动时检查可用性。
- **许可合规**：内置工具仅收录许可明确允许再分发的白名单，随包附带许可文本。

## 目录结构

```
.
├── 01-产品文档/        产品需求说明书、变更说明
├── 02-程序源码/        Python 源码（PySide6 / Qt6）
│   ├── app/           主窗口、设置对话框、入口
│   ├── core/          路径、配置、工具注册表
│   ├── data/          tools.json（130 个工具清单）
│   ├── requirements.txt
│   └── toolbox.spec   PyInstaller 打包配置（onedir）
├── 03-资源文件/        内置工具下载/展开脚本与 exe 路径映射
├── 04-安装包/          Inno Setup 脚本（仅 x64）
├── 05-官网/            官网静态页面 index.html
└── 06-测试与日志/      各版本测试报告
```

> 第三方工具二进制、PyInstaller 构建产物与安装包不在本仓库内（见 `.gitignore`）。

## 从源码运行

需要 Python 3.13（x64）：

```bash
cd 02-程序源码
pip install -r requirements.txt
python -m app.main
```

## 从源码构建

1. 用 PyInstaller 按 `toolbox.spec` 打包（onedir）：

   ```bash
   pyinstaller toolbox.spec
   ```

2. 将 `dist/` 产物与 `03-资源文件/builtin-payload/` 中的 30 个内置工具放入安装包源目录。
3. 用 `04-安装包/toolbox-x64.iss` 通过 Inno Setup 6 编译，生成 x64 安装包。

内置工具的下载与展开脚本位于 `03-资源文件/`（`fetch_*.py`、`rebuild_builtin.py`），
`builtin_exe_map.json` 记录每个内置工具主程序的准确路径。

## 许可

本软件自身源代码采用 [MIT License](LICENSE)。

仓库中的工具清单只记录第三方工具的名称、来源与许可信息，不包含其二进制文件。
内置与可下载的第三方工具分别遵循其各自的原始许可（MIT / GPL / LGPL / Apache / BSD / PSF 等），
许可文本随官方安装包附带，版权归各自所有者所有。本仓库不也无法重新授权这些第三方工具。
