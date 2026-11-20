# -*- coding: utf-8 -*-
"""重建内置工具载荷：下载 25 个新增工具 + 展开 + 探测 exe 路径 + 生成映射。

已有 5 个（VSCodium/Python/Git/7-Zip/Notepad++）已展开，本脚本只处理新增的 25 个。
输出：builtin_exe_map.json —— tools.json 的 builtin_path 以此为准，避免手写路径出错。
"""
import os
import sys
import json
import zipfile
import shutil
import urllib.request
import time

BASE = os.path.dirname(os.path.abspath(__file__))
DL = os.path.join(BASE, "builtin")
OUT = os.path.join(BASE, "builtin-payload")
os.makedirs(DL, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# (id, filename, url, [exe 候选名], version, license, category, description)
NEW_TOOLS = [
    ("neovim", "nvim-win64.zip", "https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-win64.zip", ["nvim.exe"], "0.12.6", "Apache-2.0", "文本编辑器", "Vim 的现代分支，原生 LSP"),
    ("ripgrep", "ripgrep.zip", "https://github.com/BurntSushi/ripgrep/releases/download/15.2.0/ripgrep-15.2.0-x86_64-pc-windows-msvc.zip", ["rg.exe"], "15.2.0", "MIT", "搜索工具", "极快的递归文本搜索"),
    ("fd", "fd.zip", "https://github.com/sharkdp/fd/releases/download/v10.5.2/fd-v10.5.2-x86_64-pc-windows-msvc.zip", ["fd.exe"], "10.5.2", "MIT", "搜索工具", "用户友好的 find 替代品"),
    ("bat", "bat.zip", "https://github.com/sharkdp/bat/releases/download/v0.26.1/bat-v0.26.1-x86_64-pc-windows-msvc.zip", ["bat.exe"], "0.26.1", "MIT", "文本工具", "带语法高亮的 cat 替代品"),
    ("fzf", "fzf.zip", "https://github.com/junegunn/fzf/releases/download/v0.75.0/fzf-0.75.0-windows_amd64.zip", ["fzf.exe"], "0.75.0", "MIT", "搜索工具", "交互式模糊查找器"),
    ("delta", "delta.zip", "https://github.com/dandavison/delta/releases/download/0.21.1/delta-0.21.1-x86_64-pc-windows-msvc.zip", ["delta.exe"], "0.21.1", "MIT", "版本控制", "Git diff 语法高亮查看器"),
    ("hugo", "hugo.zip", "https://github.com/gohugoio/hugo/releases/download/v0.170.1/hugo_0.170.1_windows-amd64.zip", ["hugo.exe"], "0.170.1", "BSD-2-Clause", "建站工具", "高性能静态站点生成器"),
    ("jq", "jq-win64.exe", "https://github.com/jqlang/jq/releases/download/jq-1.8.2/jq-win64.exe", ["jq-win64.exe"], "1.8.2", "MIT", "数据工具", "命令行 JSON 处理器"),
    ("cmder", "cmder_mini.zip", "https://github.com/cmderdev/cmder/releases/download/v1.3.26/cmder_mini.zip", ["Cmder.exe"], "1.3.26", "MIT", "终端工具", "Windows 增强控制台"),
    ("lazygit", "lazygit.zip", "https://github.com/jesseduffield/lazygit/releases/download/v0.66.3/lazygit_0.66.3_windows_x86_64.zip", ["lazygit.exe"], "0.66.3", "MIT", "版本控制", "终端 Git GUI"),
    ("zstd", "zstd.zip", "https://github.com/meta/zstd/releases/download/v1.5.7/zstd-v1.5.7-win64.zip", ["zstd.exe"], "1.5.7", "BSD-3-Clause", "压缩工具", "高性能压缩算法"),
    ("thonny", "thonny.zip", "https://github.com/thonny/thonny/releases/download/v5.0.1/thonny-5.0.1-windows-portable-x64.zip", ["thonny.exe"], "5.0.1", "MIT", "IDE", "Python 入门 IDE（便携版）"),
    ("notepad4", "notepad4.zip", "https://github.com/zufuliu/notepad4/releases/download/v26.10r6392/Notepad4_en_x64_v26.10r6392.zip", ["Notepad4.exe", "Notepad4_x64.exe"], "26.10", "BSD-3-Clause", "文本编辑器", "轻量文本/代码编辑器"),
    ("deno", "deno.zip", "https://github.com/denoland/deno/releases/download/v2.9.8/deno-x86_64-pc-windows-msvc.zip", ["deno.exe"], "2.9.8", "MIT", "运行环境", "安全的 JS/TS 运行时"),
    ("bun", "bun.zip", "https://github.com/oven-sh/bun/releases/download/bun-v1.4.5/bun-windows-x64.zip", ["bun.exe"], "1.4.5", "MIT", "运行环境", "高性能 JS 运行时与打包器"),
    ("hyperfine", "hyperfine.zip", "https://github.com/sharkdp/hyperfine/releases/download/v2.0.0/hyperfine-v2.0.0-x86_64-pc-windows-msvc.zip", ["hyperfine.exe"], "2.0.0", "MIT", "测试工具", "命令行基准测试工具"),
    ("micro", "micro.zip", "https://github.com/zyedidia/micro/releases/download/v2.0.15/micro-2.0.15-win64.zip", ["micro.exe"], "2.0.15", "MIT", "文本编辑器", "易用的终端文本编辑器"),
    ("lsd", "lsd.zip", "https://github.com/lsd-rs/lsd/releases/download/v1.2.0/lsd-v1.2.0-x86_64-pc-windows-msvc.zip", ["lsd.exe"], "1.2.0", "MIT", "终端工具", "带图标色彩的 ls 替代品"),
    ("procs", "procs.zip", "https://github.com/dalance/procs/releases/download/v0.14.12/procs-v0.14.12-x86_64-windows.zip", ["procs.exe"], "0.14.12", "MIT", "运维工具", "现代 ps 进程查看器"),
    ("glow", "glow.zip", "https://github.com/charmbracelet/glow/releases/download/v3.0.0/glow_3.0.0_Windows_x86_64.zip", ["glow.exe"], "3.0.0", "MIT", "文本工具", "终端 Markdown 阅读器"),
    ("zoxide", "zoxide.zip", "https://github.com/ajeetdsouza/zoxide/releases/download/v0.10.0/zoxide-0.10.0-x86_64-pc-windows-msvc.zip", ["zoxide.exe"], "0.10.0", "MIT", "终端工具", "智能目录跳转"),
    ("starship", "starship.zip", "https://github.com/starship/starship/releases/download/v1.27.0/starship-x86_64-pc-windows-msvc.zip", ["starship.exe"], "1.27.0", "MIT", "终端工具", "跨 shell 提示符"),
    ("lazydocker", "lazydocker.zip", "https://github.com/jesseduffield/lazydocker/releases/download/v0.25.2/lazydocker_0.25.2_Windows_x86_64.zip", ["lazydocker.exe"], "0.25.2", "MIT", "运维工具", "终端 Docker GUI"),
    ("scc", "scc.zip", "https://github.com/boyter/scc/releases/download/v4.1.0/scc_Windows_x86_64.zip", ["scc.exe"], "4.1.0", "MIT", "统计工具", "超快代码行数统计"),
    ("fastfetch", "fastfetch.zip", "https://github.com/fastfetch-cli/fastfetch/releases/download/2.71.0/fastfetch-windows-amd64.zip", ["fastfetch.exe"], "2.71.0", "MIT", "运维工具", "系统信息查询工具"),
]

UA = {"User-Agent": "toolbox-builder/1.0"}

def head_ok(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status < 400
    except Exception:
        return None  # HEAD 不支持时交由下载阶段验证

def download(url, path, retries=3):
    last = ""
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r, open(path, "wb") as f:
                while True:
                    chunk = r.read(1 << 18)
                    if not chunk:
                        break
                    f.write(chunk)
            return os.path.getsize(path)
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
            time.sleep(2)
    raise RuntimeError(last)

def find_exe(root, names):
    for name in names:
        for dp, _dirs, files in os.walk(root):
            for fn in files:
                if fn.lower() == name.lower():
                    return os.path.relpath(os.path.join(dp, fn), root).replace("\\", "/")
    return None

def main():
    mapping = {}
    report = []
    for (tid, fname, url, exe_names, ver, lic, cat, desc) in NEW_TOOLS:
        dest_file = os.path.join(DL, fname)
        out_dir = os.path.join(OUT, tid)
        try:
            if not os.path.exists(dest_file) or os.path.getsize(dest_file) < 1000:
                # 下载已由外部 curl（走镜像）完成；这里兜底用直链重试一次
                size = download(url, dest_file)
                print(f"[DL ] {tid:12} {size/1048576:.1f} MB", flush=True)
            else:
                print(f"[SKIP-DL] {tid:12} 已存在 {os.path.getsize(dest_file)/1048576:.1f}MB", flush=True)
            os.makedirs(out_dir, exist_ok=True)
            if dest_file.lower().endswith(".zip"):
                with zipfile.ZipFile(dest_file) as z:
                    z.extractall(out_dir)
            else:
                shutil.copy2(dest_file, os.path.join(out_dir, fname))
            rel = find_exe(out_dir, exe_names)
            if not rel:
                raise RuntimeError(f"展开后未找到 exe {exe_names}")
            mapping[tid] = {
                "builtin_path": f"builtin/{tid}/{rel}",
                "version": ver, "license": lic, "category": cat, "description": desc,
            }
            report.append((tid, "OK", rel))
            print(f"[OK ] {tid:12} -> {rel}", flush=True)
        except Exception as e:
            report.append((tid, "FAIL", str(e)[:120]))
            print(f"[FAIL] {tid:12} {type(e).__name__}: {str(e)[:120]}", flush=True)

    # 合并已有 5 个的映射
    existing = {
        "vscodium": "builtin/VSCodium/VSCodium.exe",
        "python": "builtin/Python/python.exe",
        "git": "builtin/Git/bin/git.exe",
        "sevenzip": "builtin/7-Zip/7z.exe",
        "notepadpp": "builtin/Notepad++/notepad++.exe",
    }
    for tid, p in existing.items():
        full = os.path.join(OUT, p.split("/", 1)[1])
        mapping[tid] = {"builtin_path": p, "exists": os.path.exists(full)}

    map_path = os.path.join(BASE, "builtin_exe_map.json")
    json.dump(mapping, open(map_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    ok = sum(1 for r in report if r[1] == "OK")
    print(f"=== 完成 {ok}/{len(NEW_TOOLS)} 新增工具成功；映射已写入 {map_path} ===", flush=True)
    for tid, st, info in report:
        if st == "FAIL":
            print(f"  需要人工补: {tid}: {info}", flush=True)

if __name__ == "__main__":
    main()
