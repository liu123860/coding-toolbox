# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec：编程工具箱神器 Beta v0.3（仅 x64）。

避坑要点（来自调研）：
- onedir 模式：启动快、杀软误报率低；
- 禁用 UPX：避免“堆栈缓冲区溢出”类误报；
- 排除未使用的 Qt 大模块（WebEngine/3D/Quick 等）：体积从 200MB 级压到可接受范围；
- 附完整版本信息（version.txt）：降低 SmartScreen/杀软误报。
"""

block_cipher = None

excludes = [
    # Qt 未使用的大模块
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
    "PySide6.QtWebChannel", "PySide6.QtWebSockets", "PySide6.QtWebView",
    "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DInput", "PySide6.Qt3DLogic",
    "PySide6.Qt3DAnimation", "PySide6.Qt3DExtras",
    "PySide6.QtQuick", "PySide6.QtQuickWidgets", "PySide6.QtQml", "PySide6.QtQuickControls2",
    "PySide6.QtCharts", "PySide6.QtDataVisualization", "PySide6.QtGraphs",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
    "PySide6.QtBluetooth", "PySide6.QtNfc", "PySide6.QtPositioning", "PySide6.QtLocation",
    "PySide6.QtSensors", "PySide6.QtSerialPort", "PySide6.QtSerialBus",
    "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtRemoteObjects",
    "PySide6.QtScxml", "PySide6.QtSpeech", "PySide6.QtTextToSpeech",
    "PySide6.QtTest", "PySide6.QtVirtualKeyboard", "PySide6.QtShaderTools",
    # 其他常见未用库
    "numpy", "pandas", "matplotlib", "PIL", "unittest", "test",
]

a = Analysis(
    ["app/main.py"],
    pathex=["."],
    binaries=[],
    datas=[("data/tools.json", "data")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ToolboxApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,            # 关键：禁用 UPX，避免杀软误报
    console=False,        # GUI 程序，不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version="build/version.txt",  # 完整版本信息，降低误报
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="ToolboxApp",
)
