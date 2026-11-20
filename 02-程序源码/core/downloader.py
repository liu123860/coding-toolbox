"""下载模块：后台线程下载文件到临时下载目录，带进度与失败重试。"""
import os
import time
import urllib.request

from PySide6.QtCore import QThread, Signal

from .logger import get_logger

logger = get_logger(__name__)


class DownloadWorker(QThread):
    progress = Signal(int)          # 0-100
    finished_ok = Signal(str)       # 文件保存路径
    failed = Signal(str)            # 错误信息

    def __init__(self, url: str, dest_dir: str, filename: str = "", retries: int = 2, parent=None):
        super().__init__(parent)
        self.url = url
        self.dest_dir = dest_dir
        self.retries = retries
        if not filename:
            filename = os.path.basename(url.split("?")[0]) or "download.bin"
        self.filepath = os.path.join(dest_dir, filename)

    def run(self):
        os.makedirs(self.dest_dir, exist_ok=True)
        last_err = ""
        for attempt in range(self.retries + 1):
            try:
                self._download_once()
                logger.info("下载完成：%s", self.filepath)
                self.finished_ok.emit(self.filepath)
                return
            except Exception as exc:  # noqa: BLE001 - 网络异常统一兜底
                last_err = str(exc)
                logger.warning("下载第 %d 次失败：%s", attempt + 1, last_err)
                time.sleep(1)
        self.failed.emit(last_err)

    def _download_once(self):
        req = urllib.request.Request(self.url, headers={"User-Agent": "ToolboxAlpha/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp, open(self.filepath, "wb") as out:
            total = int(resp.headers.get("Content-Length") or 0)
            downloaded = 0
            while True:
                chunk = resp.read(65536)
                if not chunk:
                    break
                out.write(chunk)
                downloaded += len(chunk)
                if total > 0:
                    self.progress.emit(int(downloaded * 100 / total))
        self.progress.emit(100)
