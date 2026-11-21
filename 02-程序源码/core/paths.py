"""统一路径解析：区分开发模式与 PyInstaller 冻结（打包）模式。

冻结模式下的两个关键原则（对应打包常见坑）：
1. 只读资源（data/tools.json）走 sys._MEIPASS，不能再用 __file__ 相对路径；
2. 可写数据（配置/安装/下载/归档）默认放 %LOCALAPPDATA%，
   避免安装到 Program Files 后普通用户无写入权限。
"""
import os
import sys


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def bundle_dir() -> str:
    """只读资源根目录（tools.json 等随 PyInstaller 打进 _MEIPASS 的数据）。"""
    if is_frozen():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def app_root() -> str:
    """程序安装根目录（安装包把预置内置工具放在这里的 builtin 目录下）。

    冻结模式不能用 _MEIPASS 作为此处基准：onedir 打包后 _MEIPASS 指向
    {app}/_internal，而 Inno 会把预置工具放在 {app}/builtin，
    两者是兄弟目录，因此基准必须是 exe 所在目录。
    """
    if is_frozen():
        return os.path.dirname(sys.executable)
    return bundle_dir()


def user_root() -> str:
    """可写数据根目录。"""
    if is_frozen():
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        return os.path.join(base, "计算机人员专业工具箱")
    return os.path.dirname(bundle_dir())
