"""日志模块：运行日志按日期滚动，统一备份到 L 盘项目目录。"""
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

BACKUP_ROOT_CANDIDATES = [
    r"L:\WorkBuddy临时文件\编程工具箱神器",
]


def resolve_backup_root() -> str:
    """统一使用 L 盘 WorkBuddy临时文件 下的项目目录；不可用时降级到本地备用目录。"""
    for candidate in BACKUP_ROOT_CANDIDATES:
        try:
            os.makedirs(candidate, exist_ok=True)
            probe = os.path.join(candidate, ".probe")
            with open(probe, "w", encoding="utf-8") as f:
                f.write("ok")
            os.remove(probe)
            return candidate
        except OSError:
            continue
    return os.path.join(os.getcwd(), "logs")


def get_logger(name: str = "toolbox") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    backup_root = resolve_backup_root()
    log_dir = os.path.join(backup_root, "logs", datetime.now().strftime("%Y-%m"))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

    handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8"
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    )
    logger.addHandler(console)

    logger.info("日志系统初始化，备份根目录：%s", backup_root)
    return logger
