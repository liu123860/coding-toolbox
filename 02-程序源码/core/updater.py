"""更新检查模块：从自有服务器拉取工具清单，比对新增/更新/下架。

合规红线：只访问 manifest_url（自有服务器 JSON），绝不爬取第三方网站。
"""
import json
import urllib.request
from typing import Dict, List

from .logger import get_logger

logger = get_logger(__name__)


def fetch_remote_manifest(manifest_url: str, timeout: int = 10) -> Dict:
    if not manifest_url:
        raise ValueError("未配置更新源地址（manifest_url）")
    req = urllib.request.Request(manifest_url, headers={"User-Agent": "ToolboxAlpha/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def diff_manifests(local: List[Dict], remote: List[Dict]) -> Dict[str, List[Dict]]:
    """比对本地与远程清单，返回新增/更新/下架三类差异。"""
    local_map = {t.get("id"): t for t in local}
    remote_map = {t.get("id"): t for t in remote}

    added = [t for tid, t in remote_map.items() if tid not in local_map]
    removed = [t for tid, t in local_map.items() if tid not in remote_map]
    updated = [
        t for tid, t in remote_map.items()
        if tid in local_map and local_map[tid].get("version") != t.get("version")
    ]
    return {"added": added, "updated": updated, "removed": removed}
