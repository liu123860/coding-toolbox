"""日志模块：运行日志按日期滚动，统一写到程序目录内的预留目录。"""
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from core.paths import app_root


def resolve_backup_root() -> str:
    """所有数据落在程序目录内的 toolbox 下，不依赖任何外部盘符。"""
    root = os.path.join(app_root(), "toolbox")
    try:
        os.makedirs(root, exist_ok=True)
        probe = os.path.join(root, ".probe")
        with open(probe, "w", encoding="utf-8") as f:
            f.write("ok")
        os.remove(probe)
        return root
    except OSError:
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
