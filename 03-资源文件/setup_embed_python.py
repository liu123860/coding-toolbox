#!/usr/bin/env python
"""构建内置 Python 运行时：embeddable Python + PySide6-Essentials。

用法（任意有网的电脑）：
    python 03-资源文件/setup_embed_python.py --dest "目标程序目录/python"

完成后目标目录内自带 python.exe/pythonw.exe 与 PySide6，
启动器 bat 优先用它，目标机器无需安装 Python。

技术要点（踩过的坑）：
1. embeddable 包默认禁用 site-packages，必须改 python313._pth：
   去掉 #import site 注释，并加一行 Lib\\site-packages，否则装了库也 import 不到。
2. PySide6 全量含 WebEngine 约 658MB，本程序只用 QtCore/QtGui/QtWidgets，
   故只装 PySide6-Essentials（约 82MB）+ shiboken6。
3. 轮子选 cp310-abi3-win_amd64，兼容 Python 3.10~3.13。
"""
import argparse
import os
import sys
import tempfile
import urllib.request
import zipfile

EMBED_URL = "https://www.python.org/ftp/python/3.13.14/python-3.13.14-embed-amd64.zip"
WHEELS = [
    ("pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl",
     "https://files.pythonhosted.org/packages/03/61/9a7e32a37b224f68506785bfb0f288d516098ec71681782d72b695a6c95d/"
     "pyside6_essentials-6.12.0-cp310-abi3-win_amd64.whl"),
    ("shiboken6-6.12.0-cp310-abi3-win_amd64.whl",
     "https://files.pythonhosted.org/packages/2a/b6/bee97e7a2edeab72aafabb46ee5adc939790a638d107860b4cad7a20e407/"
     "shiboken6-6.12.0-cp310-abi3-win_amd64.whl"),
]


def download(url: str, dest: str):
    print(f"下载 {url.split('/')[-1]} ...", flush=True)
    urllib.request.urlretrieve(url, dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", required=True, help="内置 python 的目标目录（如 盘符/程序/python）")
    args = ap.parse_args()
    dest = os.path.abspath(args.dest)
    os.makedirs(dest, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        embed_zip = os.path.join(tmp, "embed.zip")
        download(EMBED_URL, embed_zip)
        with zipfile.ZipFile(embed_zip) as z:
            z.extractall(dest)

        # 关键坑修复：启用 site-packages
        pth = os.path.join(dest, "python313._pth")
        with open(pth, "w", encoding="utf-8", newline="\n") as f:
            f.write("python313.zip\n.\nLib\\site-packages\nimport site\n")

        site = os.path.join(dest, "Lib", "site-packages")
        os.makedirs(site, exist_ok=True)
        for name, url in WHEELS:
            whl = os.path.join(tmp, name)
            download(url, whl)
            with zipfile.ZipFile(whl) as z:
                z.extractall(site)

    py = os.path.join(dest, "python.exe")
    if not os.path.exists(py):
        print("python.exe 未生成", file=sys.stderr)
        sys.exit(1)

    # 自检：必须能 import PySide6
    import subprocess
    check = subprocess.run(
        [py, "-c", "import sys; from PySide6.QtWidgets import QApplication; print(sys.version)"],
        capture_output=True, text=True)
    if check.returncode != 0:
        print("自检失败:\n" + check.stderr, file=sys.stderr)
        sys.exit(1)
    print("自检通过:", check.stdout.strip())
    print("内置 Python 构建完成:", dest)


if __name__ == "__main__":
    main()
