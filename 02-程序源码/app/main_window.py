"""主窗口：工具中心（按档位）、内置启动、按需下载、启动检查、退出处理。"""
import os
import subprocess
import sys

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QHBoxLayout, QLabel, QMessageBox,
    QProgressBar, QHeaderView, QAbstractItemView, QLineEdit,
)

from core.config import ConfigManager
from core.downloader import DownloadWorker
from core.freezer import freeze_userdata, remove_from_download_dir
from core.logger import get_logger
from core.paths import bundle_dir
from core.registry import ToolRegistry
from core.updater import fetch_remote_manifest, diff_manifests
from app.settings_dialog import SettingsDialog

logger = get_logger(__name__)

BASE_DIR = bundle_dir()
VERSION = "Beta v0.3"
# 视为「可直接下载的文件」的扩展名；其余 download_url 视为网页，用浏览器打开
FILE_EXT = (".exe", ".zip", ".msi", ".7z", ".rar", ".tar.gz", ".dmg", ".pkg")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"编程工具箱神器 {VERSION}")
        self.resize(1000, 640)

        self.cfg = ConfigManager()
        self.registry = ToolRegistry(os.path.join(BASE_DIR, "data", "tools.json"))
        self.downloads = {}       # tool_id -> DownloadWorker
        self.running_tools = {}   # tool_id -> userdata_dir

        self._build_ui()
        self._startup_check()
        self._refresh_tables()

    # ---------- UI ----------
    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("搜索工具名称 / 类别…")
        self.search.textChanged.connect(self._refresh_tables)
        self.tier_label = QLabel()
        btn_settings = QPushButton("设置")
        btn_settings.clicked.connect(self._open_settings)
        btn_update = QPushButton("检查更新")
        btn_update.clicked.connect(self._check_updates)
        top.addWidget(QLabel("搜索："))
        top.addWidget(self.search, 1)
        top.addWidget(self.tier_label)
        top.addWidget(btn_settings)
        top.addWidget(btn_update)
        layout.addLayout(top)

        self.tabs = QTabWidget()
        self.builtin_table = self._make_table(
            ["名称", "类别", "版本", "许可", "状态", "说明"])
        self.download_table = self._make_table(
            ["名称", "类别", "版本", "许可", "状态", "说明"])
        self.download_tab = QWidget()
        dl_layout = QVBoxLayout(self.download_tab)
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.dl_label = QLabel("暂无下载任务")
        dl_layout.addWidget(self.dl_label)
        dl_layout.addWidget(self.progress)
        dl_layout.addStretch(1)

        self.tabs.addTab(self.builtin_table, "内置工具")
        self.tabs.addTab(self.download_table, "可下载工具")
        self.tabs.addTab(self.download_tab, "下载任务")
        layout.addWidget(self.tabs)

        btns = QHBoxLayout()
        btn_launch = QPushButton("启动 / 下载选中工具")
        btn_launch.clicked.connect(self._launch_selected)
        btn_folder = QPushButton("打开下载目录")
        btn_folder.clicked.connect(self._open_download_dir)
        btn_site = QPushButton("打开官网")
        btn_site.clicked.connect(self._open_website)
        btns.addWidget(btn_launch)
        btns.addWidget(btn_folder)
        btns.addWidget(btn_site)
        btns.addStretch(1)
        layout.addLayout(btns)

        self.setCentralWidget(central)

    def _make_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def _fill_table(self, table, tools, status_fn):
        keyword = self.search.text().strip().lower()
        shown = [t for t in tools if not keyword
                 or keyword in t.get("name", "").lower()
                 or keyword in t.get("category", "").lower()]
        table.setRowCount(len(shown))
        for row, tool in enumerate(shown):
            values = [tool.get("name", ""), tool.get("category", ""),
                      tool.get("version", ""), tool.get("license", ""),
                      status_fn(tool), tool.get("description", "")]
            for col, val in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(str(val)))
            tool["_row"] = row
        table._shown_tools = shown

    def _refresh_tables(self):
        tier = int(self.cfg.get("tier", 30))
        self.tier_label.setText(f"当前档位：{tier} / 130")
        active = self.registry.tools_for_tier(tier)
        builtin = [t for t in active if t.get("source") == "builtin"]
        download = [t for t in active if t.get("source") in ("download", "link")]

        def builtin_status(tool):
            exe = self.registry.builtin_executable(tool, self.cfg.get("install_dir", ""))
            return "可用" if exe and os.path.exists(exe) else "未安装"

        def download_status(tool):
            local = self._downloaded_exe(tool)
            return "已下载" if local else ("下载中" if tool["id"] in self.downloads else "未下载")

        self._fill_table(self.builtin_table, builtin, builtin_status)
        self._fill_table(self.download_table, download, download_status)

    # ---------- 启动检查 ----------
    def _startup_check(self):
        # 首次启动时自动创建默认目录，避免弹出"目录不存在"警告
        for key in ("install_dir", "download_dir", "archive_dir"):
            path = self.cfg.get(key, "")
            if path:
                try:
                    os.makedirs(path, exist_ok=True)
                except OSError:
                    pass
        problems = self.cfg.check_directories()
        for p in problems:
            logger.error("目录检查失败：%s (%s) - %s", p["key"], p["path"], p["reason"])
        if problems:
            text = "\n\n".join(
                f"• {p['path']}\n  原因：{p['reason']}\n  建议：{p['suggestion']}"
                for p in problems)
            QMessageBox.warning(self, "启动检查未通过", "以下目录存在问题：\n\n" + text)
        else:
            logger.info("启动目录检查全部通过")

    # ---------- 工具选择 ----------
    def _selected_tool(self):
        table = self.tabs.currentWidget()
        if table not in (self.builtin_table, self.download_table):
            return None
        row = table.currentRow()
        if row < 0:
            return None
        shown = getattr(table, "_shown_tools", [])
        return shown[row] if row < len(shown) else None

    def _downloaded_exe(self, tool):
        """在下载目录里找该工具已下载的主程序。"""
        dest = os.path.join(self.cfg.get("download_dir", ""), tool["id"])
        if not os.path.isdir(dest):
            return ""
        exes = []
        for dp, _dirs, files in os.walk(dest):
            for fn in files:
                if fn.lower().endswith(".exe"):
                    exes.append(os.path.join(dp, fn))
        if not exes:
            return ""
        # 优先与工具 id 或名称相近的 exe
        key = tool["id"].lower().replace("-", "")
        for e in exes:
            if key in os.path.basename(e).lower().replace("-", ""):
                return e
        return exes[0]

    # ---------- 行为 ----------
    def _launch_selected(self):
        tool = self._selected_tool()
        if not tool:
            QMessageBox.information(self, "提示", "请先在列表中选中一个工具。")
            return
        if tool.get("source") == "builtin":
            self._launch_builtin(tool)
        else:
            self._handle_download_tool(tool)

    def _launch_builtin(self, tool):
        exe = self.registry.builtin_executable(tool, self.cfg.get("install_dir", ""))
        if not os.path.exists(exe):
            QMessageBox.warning(self, "工具缺失",
                                f"{tool['name']} 未找到主程序：\n{exe}")
            return
        userdata_dir = os.path.join(self.cfg.get("install_dir", ""), "userdata", tool["id"])
        os.makedirs(userdata_dir, exist_ok=True)
        try:
            subprocess.Popen([exe], cwd=os.path.dirname(exe))
            self.running_tools[tool["id"]] = userdata_dir
            logger.info("已启动工具：%s", tool["name"])
        except OSError as exc:
            QMessageBox.critical(self, "启动失败", str(exc))

    def _handle_download_tool(self, tool):
        local = self._downloaded_exe(tool)
        if local:
            try:
                subprocess.Popen([local], cwd=os.path.dirname(local))
                self.running_tools[tool["id"]] = os.path.join(
                    self.cfg.get("install_dir", ""), "userdata", tool["id"])
                os.makedirs(self.running_tools[tool["id"]], exist_ok=True)
                logger.info("已启动已下载工具：%s", tool["name"])
            except OSError as exc:
                QMessageBox.critical(self, "启动失败", str(exc))
            return

        url = tool.get("download_url") or tool.get("website")
        if tool["id"] in self.downloads:
            QMessageBox.information(self, "提示", f"{tool['name']} 正在下载中。")
            return
        is_file = url.lower().split("?")[0].endswith(FILE_EXT)
        if not is_file:
            # 下载页/在线服务：打开官网，并告知应保存到的目录
            dest = os.path.join(self.cfg.get("download_dir", ""), tool["id"])
            QDesktopServices.openUrl(QUrl(url))
            QMessageBox.information(
                self, "请从官方下载",
                f"「{tool['name']}」需从官网获取安装文件。\n已为你打开官方页面。\n\n"
                f"请下载程序后，将其放入以下目录以便工具箱统一管理：\n{dest}")
            return
        self._start_download(tool, url)

    def _start_download(self, tool, url):
        dest = os.path.join(self.cfg.get("download_dir", ""), tool["id"])
        worker = DownloadWorker(url, dest, parent=self)
        worker.progress.connect(self.progress.setValue)
        worker.finished_ok.connect(lambda p, t=tool: self._download_done(t, p))
        worker.failed.connect(lambda e, t=tool: self._download_failed(t, e))
        self.downloads[tool["id"]] = worker
        self.dl_label.setText(f"正在下载：{tool['name']} ← {url}")
        self.tabs.setCurrentWidget(self.download_tab)
        worker.start()

    def _download_done(self, tool, path):
        # 若下载的是压缩包，尝试自动解压到同目录
        if path.lower().endswith((".zip", ".7z", ".rar")):
            self._extract_archive(path, os.path.dirname(path))
        self.dl_label.setText(f"下载完成：{path}")
        self.downloads.pop(tool["id"], None)
        self._refresh_tables()
        QMessageBox.information(self, "下载完成",
                                f"「{tool['name']}」已下载到：\n{os.path.dirname(path)}")

    def _extract_archive(self, archive, dest):
        try:
            if archive.lower().endswith(".zip"):
                import zipfile
                with zipfile.ZipFile(archive) as z:
                    z.extractall(dest)
            else:
                # 7z/rar 用内置 7z.exe 解压
                from core.paths import app_root
                candidate = os.path.join(app_root(), "builtin", "7-Zip", "7z.exe")
                if os.path.exists(candidate):
                    subprocess.run([candidate, "x", "-y", f"-o{dest}", archive],
                                   capture_output=True, timeout=300)
        except Exception as exc:  # noqa: BLE001
            logger.warning("自动解压失败：%s", exc)

    def _download_failed(self, tool, err):
        self.dl_label.setText(f"下载失败：{tool['name']} - {err}")
        self.downloads.pop(tool["id"], None)
        QMessageBox.warning(self, "下载失败", f"{tool['name']} 下载失败：\n{err}")

    def _open_download_dir(self):
        dest = self.cfg.get("download_dir", "")
        os.makedirs(dest, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(dest))

    def _open_website(self):
        tool = self._selected_tool()
        if tool:
            QDesktopServices.openUrl(QUrl(tool.get("website", "")))

    def _open_settings(self):
        dlg = SettingsDialog(self.cfg, self)
        if dlg.exec():
            self._startup_check()
            self._refresh_tables()

    def _check_updates(self):
        try:
            remote = fetch_remote_manifest(self.cfg.get("manifest_url", ""))
            diff = diff_manifests(self.registry.tools, remote.get("tools", []))
            msg = (
                f"清单版本：{remote.get('version', '?')}（本地 {self.registry.manifest_version}）\n"
                f"新增工具：{len(diff['added'])} 个\n"
                f"版本更新：{len(diff['updated'])} 个\n"
                f"已下架：{len(diff['removed'])} 个"
            )
            QMessageBox.information(self, "更新检查", msg)
            logger.info("更新检查完成：+%d ~%d -%d",
                        len(diff['added']), len(diff['updated']), len(diff['removed']))
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "更新检查失败", f"无法连接更新源，已使用本地清单。\n{exc}")
            logger.warning("更新检查失败：%s", exc)

    # ---------- 退出处理 ----------
    def closeEvent(self, event):
        archive_dir = self.cfg.get("archive_dir", "")
        download_dir = self.cfg.get("download_dir", "")
        for tool_id, userdata_dir in list(self.running_tools.items()):
            tool = self.registry.get(tool_id)
            name = tool.get("name", tool_id)
            ret = QMessageBox.question(
                self, "退出处理",
                f"工具「{name}」本次运行已结束。\n是否将其用户数据冻结压缩到归档目录？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ret == QMessageBox.Yes:
                zip_path = freeze_userdata(tool_id, userdata_dir, archive_dir)
                if zip_path:
                    QMessageBox.information(self, "冻结完成", f"用户数据已归档：\n{zip_path}")

            ret2 = QMessageBox.question(
                self, "退出处理",
                f"是否将「{name}」从临时下载目录删除？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if ret2 == QMessageBox.Yes:
                remove_from_download_dir(tool_id, download_dir)

        logger.info("工具箱已退出")
        event.accept()
