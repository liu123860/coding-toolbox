# -*- coding: utf-8 -*-
"""生成 130 个工具的 tools.json。

- 30 个 source=builtin：安装包真实预置，builtin_path 取自 builtin_exe_map.json（脚本探测的准确路径）
- 100 个 source=download：未预置，按需下载到设置指定目录
- tier 字段：工具在工具库中的序号（1..130），设置档位决定工具箱启用到第几个
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
MAP_PATH = os.path.join(os.path.dirname(BASE), "03-资源文件", "builtin_exe_map.json")

# 30 个内置工具（顺序即 tier 1-30），version/license/category/desc 与下载脚本一致
BUILTIN = [
    ("vscodium", "VSCodium", "代码编辑器", "VS Code 的开源合规发行版（MIT，无微软商标与遥测）", "1.143.17232", "MIT", "https://vscodium.com"),
    ("python", "Python", "编程语言", "CPython 解释器（PSF License）", "3.13.12", "PSF", "https://www.python.org"),
    ("git", "Git for Windows", "版本控制", "分布式版本控制系统（GPLv2）", "2.56.1", "GPLv2", "https://git-scm.com"),
    ("sevenzip", "7-Zip", "压缩工具", "开源压缩解压工具（LGPL）", "26.06", "LGPL", "https://www.7-zip.org"),
    ("notepadpp", "Notepad++", "文本编辑器", "开源文本/代码编辑器（GPL）", "8.9.9.1", "GPL", "https://notepad-plus-plus.org"),
    ("neovim", "Neovim", "文本编辑器", "Vim 的现代分支，原生 LSP（Apache-2.0）", "0.12.6", "Apache-2.0", "https://neovim.io"),
    ("ripgrep", "ripgrep", "搜索工具", "极快的递归文本搜索（MIT）", "15.2.0", "MIT", "https://github.com/BurntSushi/ripgrep"),
    ("fd", "fd", "搜索工具", "用户友好的 find 替代品（MIT）", "10.5.2", "MIT", "https://github.com/sharkdp/fd"),
    ("bat", "bat", "文本工具", "带语法高亮的 cat 替代品（MIT）", "0.26.1", "MIT", "https://github.com/sharkdp/bat"),
    ("fzf", "fzf", "搜索工具", "交互式模糊查找器（MIT）", "0.75.0", "MIT", "https://github.com/junegunn/fzf"),
    ("delta", "delta", "版本控制", "Git diff 语法高亮查看器（MIT）", "0.21.1", "MIT", "https://github.com/dandavison/delta"),
    ("hugo", "Hugo", "建站工具", "高性能静态站点生成器（BSD）", "0.170.1", "BSD-2-Clause", "https://gohugo.io"),
    ("jq", "jq", "数据工具", "命令行 JSON 处理器（MIT）", "1.8.2", "MIT", "https://jqlang.github.io/jq/"),
    ("cmder", "Cmder", "终端工具", "Windows 增强控制台（MIT）", "1.3.26", "MIT", "https://cmder.net"),
    ("lazygit", "lazygit", "版本控制", "终端 Git GUI（MIT）", "0.66.3", "MIT", "https://github.com/jesseduffield/lazygit"),
    ("zstd", "Zstandard", "压缩工具", "高性能压缩算法（BSD）", "1.5.7", "BSD-3-Clause", "https://facebook.github.io/zstd/"),
    ("thonny", "Thonny", "IDE", "Python 入门 IDE 便携版（MIT）", "5.0.1", "MIT", "https://thonny.org"),
    ("notepad4", "Notepad4", "文本编辑器", "轻量文本/代码编辑器（BSD）", "26.10", "BSD-3-Clause", "https://github.com/zufuliu/notepad4"),
    ("deno", "Deno", "运行环境", "安全的 JS/TS 运行时（MIT）", "2.9.8", "MIT", "https://deno.com"),
    ("bun", "Bun", "运行环境", "高性能 JS 运行时与打包器（MIT）", "1.4.5", "MIT", "https://bun.sh"),
    ("hyperfine", "hyperfine", "测试工具", "命令行基准测试工具（MIT）", "2.0.0", "MIT", "https://github.com/sharkdp/hyperfine"),
    ("micro", "micro", "文本编辑器", "易用的终端文本编辑器（MIT）", "2.0.15", "MIT", "https://micro-editor.github.io"),
    ("lsd", "lsd", "终端工具", "带图标色彩的 ls 替代品（MIT）", "1.2.0", "MIT", "https://github.com/lsd-rs/lsd"),
    ("procs", "procs", "运维工具", "现代 ps 进程查看器（MIT）", "0.14.12", "MIT", "https://github.com/dalance/procs"),
    ("glow", "glow", "文本工具", "终端 Markdown 阅读器（MIT）", "3.0.0", "MIT", "https://github.com/charmbracelet/glow"),
    ("zoxide", "zoxide", "终端工具", "智能目录跳转（MIT）", "0.10.0", "MIT", "https://github.com/ajeetdsouza/zoxide"),
    ("starship", "starship", "终端工具", "跨 shell 提示符（MIT）", "1.27.0", "MIT", "https://starship.rs"),
    ("lazydocker", "lazydocker", "运维工具", "终端 Docker GUI（MIT）", "0.25.2", "MIT", "https://github.com/jesseduffield/lazydocker"),
    ("scc", "scc", "统计工具", "超快代码行数统计（MIT）", "4.1.0", "MIT", "https://github.com/boyter/scc"),
    ("fastfetch", "fastfetch", "运维工具", "系统信息查询工具（MIT）", "2.71.0", "MIT", "https://github.com/fastfetch-cli/fastfetch"),
]

# 100 个可下载工具（tier 31-130）：id, 名称, 类别, 简介, 许可, 官网, 下载直链/下载页
DOWNLOAD = [
    ("vscode", "Visual Studio Code", "代码编辑器", "微软官方版（许可禁止捆绑再分发，按需下载）", "微软许可", "https://code.visualstudio.com", "https://code.visualstudio.com/Download"),
    ("visualstudio", "Visual Studio", "IDE", "微软集成开发环境", "微软许可", "https://visualstudio.microsoft.com", "https://visualstudio.microsoft.com/downloads/"),
    ("nodejs", "Node.js", "运行环境", "JavaScript 运行时（MIT，商标受限）", "MIT", "https://nodejs.org", "https://nodejs.org/dist/"),
    ("kimi", "Kimi", "AI 工具", "AI 助手（在线服务快捷入口）", "服务条款", "https://www.kimi.com", "https://www.kimi.com"),
    ("codex", "Codex", "AI 工具", "OpenAI Codex（在线服务入口）", "服务条款", "https://openai.com", "https://openai.com/codex/"),
    ("cursor", "Cursor", "AI 工具", "AI 原生代码编辑器", "专有", "https://cursor.com", "https://cursor.com/download"),
    ("windsurf", "Windsurf", "AI 工具", "AI 编程编辑器", "专有", "https://windsurf.com", "https://windsurf.com/download"),
    ("scratch", "Scratch", "编程启蒙", "图形化编程工具", "官方许可", "https://scratch.mit.edu", "https://scratch.mit.edu/download"),
    ("java", "OpenJDK (Temurin)", "运行环境", "Java 开发工具包", "GPL+CE", "https://adoptium.net", "https://adoptium.net/temurin/releases/"),
    ("golang", "Go", "编程语言", "Go 语言工具链", "BSD-3", "https://go.dev", "https://go.dev/dl/"),
    ("rust", "Rust", "编程语言", "Rust 工具链（rustup）", "MIT/Apache", "https://www.rust-lang.org", "https://rustup.rs/"),
    ("php", "PHP", "运行环境", "PHP 解释器", "PHP License", "https://www.php.net", "https://windows.php.net/download/"),
    ("ruby", "Ruby", "运行环境", "Ruby 解释器", "BSD-2", "https://www.ruby-lang.org", "https://rubyinstaller.org/downloads/"),
    ("perl", "Perl", "运行环境", "Strawberry Perl", "GPL/Artistic", "https://www.perl.org", "https://strawberryperl.com/download.html"),
    ("kotlin", "Kotlin", "编程语言", "Kotlin 编译器", "Apache-2.0", "https://kotlinlang.org", "https://github.com/JetBrains/kotlin/releases"),
    ("scala", "Scala", "编程语言", "Scala 编译器", "Apache-2.0", "https://www.scala-lang.org", "https://www.scala-lang.org/download/"),
    ("lua", "Lua", "编程语言", "Lua 解释器", "MIT", "https://www.lua.org", "https://www.lua.org/download.html"),
    ("r", "R", "编程语言", "R 语言环境", "GPL-2", "https://www.r-project.org", "https://cran.r-project.org/bin/windows/base/"),
    ("julia", "Julia", "编程语言", "Julia 科学计算语言", "MIT", "https://julialang.org", "https://julialang.org/downloads/"),
    ("dart", "Dart", "编程语言", "Dart SDK", "BSD-3", "https://dart.dev", "https://dart.dev/get-dart"),
    ("zig", "Zig", "编程语言", "Zig 系统编程语言", "MIT", "https://ziglang.org", "https://ziglang.org/download/"),
    ("nim", "Nim", "编程语言", "Nim 编译器", "MIT", "https://nim-lang.org", "https://nim-lang.org/install_windows.html"),
    ("gcc", "MinGW-w64", "编译器", "Windows GCC 工具链", "GPL/MIT", "https://www.mingw-w64.org", "https://www.mingw-w64.org/downloads/"),
    ("llvm", "LLVM/Clang", "编译器", "LLVM 编译器套件", "Apache-2.0", "https://llvm.org", "https://releases.llvm.org/download.html"),
    ("cmake", "CMake", "构建工具", "跨平台构建系统", "BSD-3", "https://cmake.org", "https://cmake.org/download/"),
    ("ninja", "Ninja", "构建工具", "高性能构建系统", "Apache-2.0", "https://ninja-build.org", "https://github.com/ninja-build/ninja/releases"),
    ("make", "GNU Make", "构建工具", "GNU make for Windows", "GPL-3", "https://www.gnu.org/software/make/", "https://gnuwin32.sourceforge.net/packages/make.htm"),
    ("meson", "Meson", "构建工具", "现代构建系统", "Apache-2.0", "https://mesonbuild.com", "https://mesonbuild.com/Getting-meson.html"),
    ("maven", "Maven", "构建工具", "Java 项目构建管理", "Apache-2.0", "https://maven.apache.org", "https://maven.apache.org/download.cgi"),
    ("gradle", "Gradle", "构建工具", "灵活的项目构建工具", "Apache-2.0", "https://gradle.org", "https://gradle.org/releases/"),
    ("bazel", "Bazel", "构建工具", "Google 开源构建工具", "Apache-2.0", "https://bazel.build", "https://bazel.build/install/win"),
    ("eclipse", "Eclipse IDE", "IDE", "Java/CPP 开源 IDE", "EPL-2.0", "https://www.eclipse.org", "https://www.eclipse.org/downloads/"),
    ("netbeans", "Apache NetBeans", "IDE", "Java IDE", "Apache-2.0", "https://netbeans.apache.org", "https://netbeans.apache.org/front/main/download/"),
    ("intellij", "IntelliJ IDEA CE", "IDE", "JetBrains Java IDE 社区版", "Apache-2.0", "https://www.jetbrains.com/idea/", "https://www.jetbrains.com/idea/download/"),
    ("pycharm", "PyCharm CE", "IDE", "JetBrains Python IDE 社区版", "Apache-2.0", "https://www.jetbrains.com/pycharm/", "https://www.jetbrains.com/pycharm/download/"),
    ("androidstudio", "Android Studio", "IDE", "Android 官方 IDE", "Apache-2.0", "https://developer.android.com/studio", "https://developer.android.com/studio#downloads"),
    ("arduino", "Arduino IDE", "IDE", "Arduino 开发环境", "GPL-2", "https://www.arduino.cc", "https://www.arduino.cc/en/software"),
    ("codeblocks", "Code::Blocks", "IDE", "C/C++ 开源 IDE", "GPL-3", "https://www.codeblocks.org", "https://www.codeblocks.org/downloads/binaries/"),
    ("devcpp", "Dev-C++", "IDE", "轻量 C/C++ IDE", "GPL-2", "https://sourceforge.net/projects/dev-cpp/", "https://sourceforge.net/projects/dev-cpp/files/Binaries/"),
    ("qtcreator", "Qt Creator", "IDE", "Qt 跨平台 IDE", "GPL/LGPL", "https://www.qt.io", "https://www.qt.io/download-qt-installer-oss"),
    ("goland", "GoLand", "IDE", "Go IDE", "专有", "https://www.jetbrains.com/go/", "https://www.jetbrains.com/go/download/"),
    ("webstorm", "WebStorm", "IDE", "前端 IDE", "专有", "https://www.jetbrains.com/webstorm/", "https://www.jetbrains.com/webstorm/download/"),
    ("dbeaver", "DBeaver CE", "数据库", "通用数据库客户端", "Apache-2.0", "https://dbeaver.io", "https://dbeaver.io/download/"),
    ("heidisql", "HeidiSQL", "数据库", "MySQL/MariaDB 客户端", "GPL-2", "https://www.heidisql.com", "https://www.heidisql.com/download.php"),
    ("sqlite", "SQLite Tools", "数据库", "SQLite 命令行工具", "公共领域", "https://www.sqlite.org", "https://www.sqlite.org/download.html"),
    ("mysql", "MySQL Workbench", "数据库", "MySQL 官方 GUI 工具", "GPL-2", "https://www.mysql.com", "https://dev.mysql.com/downloads/workbench/"),
    ("pgadmin", "pgAdmin", "数据库", "PostgreSQL 管理工具", "PostgreSQL", "https://www.pgadmin.org", "https://www.pgadmin.org/download/"),
    ("redis", "Redis", "数据库", "内存数据库", "BSD-3", "https://redis.io", "https://github.com/tporadowski/redis/releases"),
    ("mongodb", "MongoDB Compass", "数据库", "MongoDB GUI", "专有", "https://www.mongodb.com", "https://www.mongodb.com/try/download/compass"),
    ("postman", "Postman", "API 工具", "API 开发与测试", "专有", "https://www.postman.com", "https://www.postman.com/downloads/"),
    ("insomnia", "Insomnia", "API 工具", "开源 API 客户端", "Apache-2.0", "https://insomnia.rest", "https://insomnia.rest/download"),
    ("apifox", "Apifox", "API 工具", "API 一体化协作平台", "专有", "https://www.apifox.cn", "https://www.apifox.cn/download"),
    ("wireshark", "Wireshark", "网络工具", "网络协议分析器", "GPL-2", "https://www.wireshark.org", "https://www.wireshark.org/download.html"),
    ("putty", "PuTTY", "网络工具", "SSH/Telnet 客户端", "MIT", "https://www.putty.org", "https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html"),
    ("filezilla", "FileZilla", "网络工具", "FTP 客户端", "GPL-2", "https://filezilla-project.org", "https://filezilla-project.org/download.php"),
    ("winscp", "WinSCP", "网络工具", "SFTP/SCP 客户端", "GPL-3", "https://winscp.net", "https://winscp.net/eng/downloads.php"),
    ("ngrok", "ngrok", "网络工具", "内网穿透", "专有", "https://ngrok.com", "https://dashboard.ngrok.com/get-started/setup/windows"),
    ("curltool", "curl", "网络工具", "命令行 URL 传输工具", "curl License", "https://curl.se", "https://curl.se/windows/"),
    ("wget", "Wget", "网络工具", "命令行下载工具", "GPL-3", "https://www.gnu.org/software/wget/", "https://eternallybored.org/misc/wget/"),
    ("gimp", "GIMP", "图形图像", "开源图像编辑器", "GPL-3", "https://www.gimp.org", "https://www.gimp.org/downloads/"),
    ("inkscape", "Inkscape", "图形图像", "矢量图形编辑器", "GPL-2", "https://inkscape.org", "https://inkscape.org/release/"),
    ("krita", "Krita", "图形图像", "数字绘画工具", "GPL-3", "https://krita.org", "https://krita.org/en/download/"),
    ("blender", "Blender", "图形图像", "3D 创作套件", "GPL-3", "https://www.blender.org", "https://www.blender.org/download/"),
    ("vlc", "VLC", "多媒体", "开源媒体播放器", "GPL-2", "https://www.videolan.org", "https://www.videolan.org/vlc/download-windows.html"),
    ("obs", "OBS Studio", "多媒体", "屏幕录制与直播", "GPL-2", "https://obsproject.com", "https://obsproject.com/download"),
    ("audacity", "Audacity", "多媒体", "音频编辑器", "GPL-2", "https://www.audacityteam.org", "https://www.audacityteam.org/download/"),
    ("ffmpeg", "FFmpeg", "多媒体", "音视频处理工具", "LGPL/GPL", "https://ffmpeg.org", "https://www.gyan.dev/ffmpeg/builds/"),
    ("drawio", "draw.io", "图形图像", "流程图与图表工具", "Apache-2.0", "https://www.drawio.com", "https://www.drawio.com/doc/faq/download-desktop"),
    ("graphviz", "Graphviz", "图形图像", "图形可视化工具", "EPL-1.0", "https://graphviz.org", "https://graphviz.org/download/"),
    ("plantuml", "PlantUML", "图形图像", "UML 图生成工具", "GPL-3", "https://plantuml.com", "https://plantuml.com/download"),
    ("pandoc", "Pandoc", "文档工具", "文档格式转换", "GPL-2", "https://pandoc.org", "https://pandoc.org/installing.html"),
    ("typora", "Typora", "文档工具", "Markdown 编辑器", "专有", "https://typora.io", "https://typora.io/#download"),
    ("obsidian", "Obsidian", "文档工具", "知识库笔记工具", "专有", "https://obsidian.md", "https://obsidian.md/download"),
    ("joplin", "Joplin", "文档工具", "开源笔记工具", "MIT", "https://joplinapp.org", "https://joplinapp.org/download/"),
    ("texstudio", "TeXstudio", "文档工具", "LaTeX 编辑器", "GPL-2", "https://www.texstudio.org", "https://www.texstudio.org/#download"),
    ("miktex", "MiKTeX", "文档工具", "Windows LaTeX 发行版", "GPL-2", "https://miktex.org", "https://miktex.org/download"),
    ("docker", "Docker Desktop", "云计算", "容器运行环境", "专有", "https://www.docker.com", "https://www.docker.com/products/docker-desktop/"),
    ("podman", "Podman Desktop", "云计算", "无守护进程容器工具", "Apache-2.0", "https://podman.io", "https://podman-desktop.io/downloads"),
    ("vagrant", "Vagrant", "云计算", "虚拟机环境管理", "MIT", "https://www.vagrantup.com", "https://www.vagrantup.com/downloads"),
    ("virtualbox", "VirtualBox", "云计算", "开源虚拟机", "GPL-2", "https://www.virtualbox.org", "https://www.virtualbox.org/wiki/Downloads"),
    ("wsl", "WSL", "云计算", "Windows Linux 子系统", "微软许可", "https://learn.microsoft.com/windows/wsl/", "https://learn.microsoft.com/windows/wsl/install"),
    ("terraform", "Terraform", "云计算", "基础设施即代码", "MPL-2.0", "https://www.terraform.io", "https://developer.hashicorp.com/terraform/downloads"),
    ("ansible", "Ansible", "运维工具", "自动化运维工具", "GPL-3", "https://www.ansible.com", "https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html"),
    ("hugoext", "Hugo Extended", "建站工具", "静态站点生成器（扩展版）", "BSD-2", "https://gohugo.io", "https://github.com/gohugoio/hugo/releases"),
    ("jekyll", "Jekyll", "建站工具", "Ruby 静态站点生成器", "MIT", "https://jekyllrb.com", "https://jekyllrb.com/docs/installation/windows/"),
    ("hexo", "Hexo", "建站工具", "Node.js 博客框架", "MIT", "https://hexo.io", "https://hexo.io/docs/"),
    ("npm", "npm", "包管理", "Node.js 包管理器", "ISC", "https://www.npmjs.com", "https://nodejs.org/en/download/"),
    ("pnpm", "pnpm", "包管理", "高性能包管理器", "MIT", "https://pnpm.io", "https://pnpm.io/installation"),
    ("yarn", "Yarn", "包管理", "JavaScript 包管理器", "BSD-2", "https://yarnpkg.com", "https://yarnpkg.com/getting-started/install"),
    ("pip", "pip", "包管理", "Python 包管理器", "MIT", "https://pypi.org/project/pip/", "https://pip.pypa.io/en/stable/installation/"),
    ("conda", "Miniconda", "包管理", "Python 环境管理", "BSD-3", "https://docs.conda.io", "https://docs.conda.io/en/latest/miniconda.html"),
    ("nuget", "NuGet", "包管理", ".NET 包管理器", "Apache-2.0", "https://www.nuget.org", "https://www.nuget.org/downloads"),
    ("vcpkg", "vcpkg", "包管理", "C++ 库管理器", "MIT", "https://vcpkg.io", "https://github.com/microsoft/vcpkg"),
    ("chocolatey", "Chocolatey", "包管理", "Windows 包管理器", "Apache-2.0", "https://community.chocolatey.org", "https://chocolatey.org/install"),
    ("scoop", "Scoop", "包管理", "Windows 命令行包管理器", "MIT", "https://scoop.sh", "https://scoop.sh/"),
    ("gitbash", "Git Bash", "终端工具", "Git 自带 Unix shell", "GPL-2", "https://git-scm.com", "https://git-scm.com/download/win"),
    ("cmderfull", "Cmder Full", "终端工具", "增强控制台完整版", "MIT", "https://cmder.net", "https://github.com/cmderdev/cmder/releases"),
    ("windowsterminal", "Windows Terminal", "终端工具", "微软现代终端", "MIT", "https://learn.microsoft.com/windows/terminal/", "https://www.microsoft.com/store/apps/9N0DX20HK701"),
    ("alacritty", "Alacritty", "终端工具", "GPU 加速终端", "MIT/Apache", "https://github.com/alacritty/alacritty", "https://github.com/alacritty/alacritty/releases"),
    ("wezterm", "WezTerm", "终端工具", "GPU 加速终端复用器", "MIT/Apache", "https://wezfurlong.org/wezterm/", "https://github.com/wez/wezterm/releases"),
]

def main():
    m = json.load(open(MAP_PATH, encoding="utf-8")) if os.path.exists(MAP_PATH) else {}
    tools = []
    tier = 1
    for tid, name, cat, desc, ver, lic, web in BUILTIN:
        bp = m.get(tid, {}).get("builtin_path", "")
        tools.append({
            "id": tid, "name": name, "category": cat, "description": desc,
            "version": ver, "size": "-", "license": lic, "source": "builtin",
            "builtin_path": bp, "download_url": "", "website": web, "tier": tier,
        })
        tier += 1
    for tid, name, cat, desc, lic, web, url in DOWNLOAD:
        tools.append({
            "id": tid, "name": name, "category": cat, "description": desc,
            "version": "-", "size": "-", "license": lic, "source": "download",
            "builtin_path": "", "download_url": url, "website": web, "tier": tier,
        })
        tier += 1

    data = {
        "version": "0.3.0",
        "updated": "2026-11-19",
        "builtin_count": len(BUILTIN),
        "total_count": len(tools),
        "tiers": [30, 50, 60, 80, 100, 130],
        "tools": tools,
    }
    out = os.path.join(BASE, "data", "tools.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"写入 {out}：builtin={len(BUILTIN)} download={len(DOWNLOAD)} total={len(tools)}")
    missing = [t["id"] for t in tools if t["source"] == "builtin" and not t["builtin_path"]]
    print("内置工具缺路径（映射未就绪）:", missing)

if __name__ == "__main__":
    main()
