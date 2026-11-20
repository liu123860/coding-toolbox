# -*- coding: utf-8 -*-
"""分段下载器：用 GitHub API asset 端点 + Range 分段，专治大文件截断。

每段 4MB，逐段下载并校验总长度，全部拼完后校验 zip。
"""
import os
import json
import subprocess
import urllib.request
import zipfile
import time

DL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "builtin")
TMP = os.path.join(os.environ.get("TEMP", "/tmp"), "tbdld", "chunks")
os.makedirs(TMP, exist_ok=True)
CHUNK = 4 * 1024 * 1024  # 4MB
UA = {"User-Agent": "tbb", "Accept": "application/octet-stream"}

# fname -> (repo, asset_name)
ITEMS = {
    "bun.zip": ("oven-sh/bun", "bun-windows-x64.zip"),
    "deno.zip": ("denoland/deno", "deno-x86_64-pc-windows-msvc.zip"),
    "glow.zip": ("charmbracelet/glow", "glow_3.0.0_Windows_x86_64.zip"),
    "lazygit.zip": ("jesseduffield/lazygit", "lazygit_0.66.3_windows_x86_64.zip"),
    "micro.zip": ("zyedidia/micro", "micro-2.0.15-win64.zip"),
    "scc.zip": ("boyter/scc", "scc_Windows_x86_64.zip"),
    "thonny.zip": ("thonny/thonny", "thonny-5.0.1-windows-portable-x64.zip"),
    "fastfetch.zip": ("fastfetch-cli/fastfetch", "fastfetch-windows-amd64.zip"),
}


def get_asset(repo, name):
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/latest",
                                 headers={"User-Agent": "tbb", "Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    for a in data["assets"]:
        if a["name"] == name:
            return a["id"], a["size"]
    raise RuntimeError(f"asset not found: {name}")


def is_valid(path, expected_size=0):
    if not os.path.exists(path) or os.path.getsize(path) < 1000:
        return False
    if expected_size and os.path.getsize(path) != expected_size:
        return False
    try:
        with zipfile.ZipFile(path) as z:
            return len(z.namelist()) > 0 and z.testzip() is None
    except Exception:
        return False


def fetch_one(fname, repo, name):
    final = os.path.join(DL, fname)
    aid, size = get_asset(repo, name)
    if is_valid(final, size):
        print(f"[SKIP] {fname} 已有效 ({size/1048576:.1f}MB)", flush=True)
        return True
    # 用真实 asset url
    url = f"https://api.github.com/repos/{repo}/releases/assets/{aid}"
    chunk_dir = os.path.join(TMP, fname.replace('.zip',''))
    os.makedirs(chunk_dir, exist_ok=True)
    nchunks = (size + CHUNK - 1) // CHUNK
    print(f"[GET ] {fname} {size/1048576:.1f}MB / {nchunks} 段", flush=True)
    for i in range(nchunks):
        start = i * CHUNK
        end = min(start + CHUNK - 1, size - 1)
        cfile = os.path.join(chunk_dir, f"{i:03d}.part")
        expect = end - start + 1
        ok = False
        for attempt in range(6):
            if os.path.exists(cfile) and os.path.getsize(cfile) == expect:
                ok = True
                break
            try:
                cmd = ["curl", "-sL", "--http1.1", "--connect-timeout", "15", "--max-time", "90",
                       "-H", "Accept: application/octet-stream", "-H", "User-Agent: tbb",
                       "-r", f"{start}-{end}", "-o", cfile, url]
                subprocess.run(cmd, capture_output=True, timeout=100)
                if os.path.exists(cfile) and os.path.getsize(cfile) == expect:
                    ok = True
                    break
            except Exception:
                pass
            time.sleep(1)
        if not ok:
            print(f"[FAIL] {fname} 第 {i}/{nchunks} 段失败", flush=True)
            return False
        print(f"  seg {i+1}/{nchunks} OK", flush=True)
    # 拼接
    assembled = final + ".assembling"
    with open(assembled, "wb") as out:
        for i in range(nchunks):
            with open(os.path.join(chunk_dir, f"{i:03d}.part"), "rb") as f:
                out.write(f.read())
    if os.path.getsize(assembled) == size and is_valid(assembled, size):
        os.replace(assembled, final)
        print(f"[OK  ] {fname} 完整拼接 {size/1048576:.1f}MB", flush=True)
        return True
    print(f"[FAIL] {fname} 拼接后校验失败 ({os.path.getsize(assembled)} vs {size})", flush=True)
    return False


def main():
    import sys
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    targets = {k: v for k, v in ITEMS.items() if not only or k in only}
    ok = 0
    for fname, (repo, name) in targets.items():
        try:
            if fetch_one(fname, repo, name):
                ok += 1
        except Exception as e:
            print(f"[ERR ] {fname} {type(e).__name__}: {str(e)[:80]}", flush=True)
    print(f"=== 成功 {ok}/{len(targets)} ===", flush=True)


if __name__ == "__main__":
    main()
