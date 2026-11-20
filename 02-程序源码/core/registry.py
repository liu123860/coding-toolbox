"""工具清单注册表：读取 tools.json，区分内置与直链工具。"""
import json
import os
from typing import Dict, List

from .logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.tools: List[Dict] = []
        self.manifest_version: str = "0.0.0"
        self.load()

    def load(self):
        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.tools = data.get("tools", [])
            self.manifest_version = data.get("version", "0.0.0")
            logger.info("工具清单加载成功：%d 个工具", len(self.tools))
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("工具清单加载失败：%s", exc)
            self.tools = []

    def tools_for_tier(self, tier: int) -> List[Dict]:
        """按档位返回工具库子集（tier <= 指定档位）。"""
        try:
            t = int(tier)
        except (TypeError, ValueError):
            t = 130
        return [tool for tool in self.tools if int(tool.get("tier", 0)) <= t]

    def builtin_tools(self) -> List[Dict]:
        return [t for t in self.tools if t.get("source") == "builtin"]

    def download_tools(self) -> List[Dict]:
        return [t for t in self.tools if t.get("source") == "download"]

    def link_tools(self) -> List[Dict]:
        """兼容旧数据：既保留 source=link，也把 source=download 视为可下载工具。"""
        return [t for t in self.tools if t.get("source") in ("link", "download")]

    def get(self, tool_id: str) -> Dict:
        for t in self.tools:
            if t.get("id") == tool_id:
                return t
        return {}

    def builtin_executable(self, tool: Dict, install_dir: str) -> str:
        """解析内置工具的可执行文件路径。

        查找顺序（对应「开箱即用」）：
        1. 程序安装目录 {app}\\builtin\\ —— 安装包预置的工具，装完即可用；
        2. 设置中心指定的运行环境目录 —— 用户按需下载或迁移后的工具。
        两者都不存在时返回安装目录路径，供调用方判定为「未安装」。
        """
        rel = tool.get("builtin_path", "")
        if not rel:
            return ""
        from .paths import app_root
        candidates = [
            os.path.join(app_root(), rel),
            os.path.join(install_dir, rel) if install_dir else "",
        ]
        for path in candidates:
            if path and os.path.exists(path):
                return path
        return candidates[0]
