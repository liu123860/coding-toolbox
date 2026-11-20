"""配置模块：config.json 读写、目录健康检查、目录变更迁移。"""
import json
import os
import shutil
from typing import Dict, List, Optional

from core.paths import app_root

DEFAULT_CONFIG: Dict = {
    "install_dir": "",          # 工具箱安装目录（默认：程序目录下预留 toolbox）
    "download_dir": "",         # 软件/插件临时下载目录（默认：程序目录内）
    "archive_dir": "",          # 用户数据冻结归档目录（默认：程序目录内）
    "concurrency": 3,           # 下载并发数
    "tier": 30,                 # 工具库档位：30/50/60/80/100/130
    "manifest_url": "",         # 工具清单更新源（自有服务器 JSON）
    "log_level": "INFO",
}

DIR_KEYS = ("install_dir", "download_dir", "archive_dir")
TIER_OPTIONS = (30, 50, 60, 80, 100, 130)


def default_install_root() -> str:
    """所有默认目录都落在程序安装目录内的预留子目录（用户明确要求）。"""
    return app_root()


class ConfigManager:
    def __init__(self, config_path: Optional[str] = None):
        base = default_install_root()
        self.config_path = config_path or os.path.join(base, "config", "config.json")
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        self.config: Dict = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_cfg = json.load(f)
                self.config.update({k: v for k, v in user_cfg.items() if k in DEFAULT_CONFIG})
            except (json.JSONDecodeError, OSError):
                pass
        base = default_install_root()
        # 默认全部在程序文件目录内的预留子目录
        defaults = {
            "install_dir": os.path.join(base, "toolbox"),
            "download_dir": os.path.join(base, "toolbox", "downloads"),
            "archive_dir": os.path.join(base, "toolbox", "archives"),
        }
        for key, val in defaults.items():
            if not self.config.get(key):
                self.config[key] = val
        # 档位校验：非法值回落到 30
        if self.config.get("tier") not in TIER_OPTIONS:
            self.config["tier"] = 30

    def save(self):
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default=None):
        return self.config.get(key, default)

    def set(self, key: str, value):
        self.config[key] = value

    # ---- 目录健康检查 ----
    def check_directories(self) -> List[Dict]:
        """启动时检查所有目录。返回问题列表，空列表 = 全部正常。"""
        problems = []
        for key in DIR_KEYS:
            path = self.config.get(key, "")
            if not os.path.exists(path):
                problems.append({
                    "key": key, "path": path,
                    "reason": "目录不存在",
                    "suggestion": "请创建该目录，或在设置中心重新指定",
                })
                continue
            if not os.path.isdir(path):
                problems.append({
                    "key": key, "path": path,
                    "reason": "路径存在但不是目录",
                    "suggestion": "请在设置中心重新指定有效目录",
                })
                continue
            if not os.access(path, os.W_OK | os.R_OK):
                problems.append({
                    "key": key, "path": path,
                    "reason": "目录不可读写（权限不足）",
                    "suggestion": "请检查该目录的访问权限",
                })
        return problems

    # ---- 目录迁移 ----
    def migrate_directory(self, key: str, new_path: str) -> Dict:
        """修改目录并迁移已有文件。返回执行结果说明。"""
        old_path = self.config.get(key, "")
        result = {"migrated": False, "files": 0, "error": None}
        if old_path and os.path.exists(old_path) and old_path != new_path:
            try:
                os.makedirs(new_path, exist_ok=True)
                for item in os.listdir(old_path):
                    src = os.path.join(old_path, item)
                    dst = os.path.join(new_path, item)
                    if os.path.exists(dst):
                        continue
                    shutil.move(src, dst)
                    result["files"] += 1
                result["migrated"] = True
            except OSError as exc:
                result["error"] = str(exc)
        self.config[key] = new_path
        self.save()
        return result
