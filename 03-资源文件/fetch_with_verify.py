# -*- coding: utf-8 -*-
"""带完整性校验的下载器：调 curl 走镜像，校验 zip/exe 完整性，失败自动换镜像。

用法：python fetch_with_verify.py
- 读取 rebuild_builtin.py 里的 NEW_TOOLS
- 每个工具：若已有有效文件则跳过；否则依次尝试 3 个镜像
- zip 用 zipfile 校验；单 exe 校验 MZ 头
"""
import os
import re
import subprocess
import zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(BASE, "builtin")
SRC = os.path.join(BASE, "rebuild_builtin.py")

MIRRORS = [
    "https://gh-proxy.com/",
    "https://ghfast.top/",
    "https://gh-proxy.net/",
    "",  # 最后直连
]


def valid(path, fname):
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        return False
    if fname.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(path) as z:
                return len(z.namelist()) > 0 and z.testzip() is None
        except Exception:
            return False
    # 单文件 exe：校验 MZ 头
    with open(path, "rb") as f:
        return f.read(2) == b"MZ"


def fetch(tid, fname, url):
    final = os.path.join(DL, fname)
    if valid(final, fname):
        print(f"[SKIP] {tid:12} 已有效", flush=True)
        return True
    tmp = final + ".part"
    for m in MIRRORS:
        full = f"{m}{url}" if m else url
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
            subprocess.run(
                ["curl", "-sL", "--connect-timeout", "15", "--max-time", "120",
                 "-o", tmp, full],
                capture_output=True, timeout=130,
            )
            if valid(tmp, fname):
                os.replace(tmp, final)
                print(f"[OK  ] {tid:12} {os.path.getsize(final)/1048576:.1f}MB via {m or 'direct'}", flush=True)
                return True
            else:
                print(f"[BAD ] {tid:12} 校验失败 via {m or 'direct'}", flush=True)
        except Exception as e:
            print(f"[ERR ] {tid:12} {type(e).__name__} via {m or 'direct'}", flush=True)
    if os.path.exists(tmp):
        os.remove(tmp)
    print(f"[FAIL] {tid:12} 所有镜像均失败", flush=True)
    return False


def main():
    text = open(SRC, encoding="utf-8").read()
    entries = re.findall(r'\("([a-z0-9]+)",\s*"([^"]+)",\s*"(https://[^"]+)"', text)
    ok = 0
    for tid, fname, url in entries:
        if fetch(tid, fname, url):
            ok += 1
    print(f"=== 有效工具 {ok}/{len(entries)} ===", flush=True)


if __name__ == "__main__":
    main()
