# -*- coding: utf-8 -*-
"""顽固文件稳健下载：多源轮换 + 完整性校验，直到成功或耗尽重试。"""
import os
import subprocess
import zipfile
import sys
import time

DL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "builtin")

# fname -> official url
ITEMS = {
    "bun.zip": "https://github.com/oven-sh/bun/releases/download/bun-v1.4.5/bun-windows-x64.zip",
    "deno.zip": "https://github.com/denoland/deno/releases/download/v2.9.8/deno-x86_64-pc-windows-msvc.zip",
    "glow.zip": "https://github.com/charmbracelet/glow/releases/download/v3.0.0/glow_3.0.0_Windows_x86_64.zip",
    "lazygit.zip": "https://github.com/jesseduffield/lazygit/releases/download/v0.66.3/lazygit_0.66.3_windows_x86_64.zip",
    "micro.zip": "https://github.com/zyedidia/micro/releases/download/v2.0.15/micro-2.0.15-win64.zip",
    "scc.zip": "https://github.com/boyter/scc/releases/download/v4.1.0/scc_Windows_x86_64.zip",
    "thonny.zip": "https://github.com/thonny/thonny/releases/download/v5.0.1/thonny-5.0.1-windows-portable-x64.zip",
    "fastfetch.zip": "https://github.com/fastfetch-cli/fastfetch/releases/download/2.71.0/fastfetch-windows-amd64.zip",
}

# (label, prefix, extra curl args)
SOURCES = [
    ("gh-proxy", "https://gh-proxy.com/", ["--http1.1"]),
    ("ghfast", "https://ghfast.top/", ["--http1.1"]),
    ("direct", "", ["--http1.1"]),
    ("gh-proxy-net", "https://gh-proxy.net/", ["--http1.1"]),
]


def is_valid(path):
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        return False
    try:
        with zipfile.ZipFile(path) as z:
            return len(z.namelist()) > 0 and z.testzip() is None
    except Exception:
        return False


def fetch_one(fname, url):
    final = os.path.join(DL, fname)
    if is_valid(final):
        print(f"[SKIP] {fname}", flush=True)
        return True
    tmp = final + ".part"
    for rnd in range(3):
        for label, prefix, extra in SOURCES:
            full = f"{prefix}{url}" if prefix else url
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
                cmd = ["curl", "-sL", "--connect-timeout", "15", "--max-time", "200"] + extra + ["-o", tmp, full]
                subprocess.run(cmd, capture_output=True, timeout=210)
                if is_valid(tmp):
                    os.replace(tmp, final)
                    print(f"[OK  ] {fname:20} via {label} r{rnd} {os.path.getsize(final)/1048576:.1f}MB", flush=True)
                    return True
            except Exception as e:
                print(f"[ERR ] {fname} {label}: {type(e).__name__}", flush=True)
        print(f"[RETRY] {fname} 第 {rnd+1} 轮全失败，继续", flush=True)
    if os.path.exists(tmp):
        os.remove(tmp)
    print(f"[FAIL] {fname} 耗尽重试", flush=True)
    return False


def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    targets = {k: v for k, v in ITEMS.items() if not only or k in only}
    ok = sum(1 for f, u in targets.items() if fetch_one(f, u))
    print(f"=== 成功 {ok}/{len(targets)} ===", flush=True)


if __name__ == "__main__":
    main()
