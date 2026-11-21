"""设置窗口：目录配置、并发数、更新源；修改目录时询问是否迁移。"""
import os

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QFileDialog,
    QSpinBox, QMessageBox, QVBoxLayout, QDialogButtonBox, QComboBox,
)

from core.config import ConfigManager, DIR_KEYS, TIER_OPTIONS
from core.logger import get_logger

logger = get_logger(__name__)


class SettingsDialog(QDialog):
    def __init__(self, cfg: ConfigManager, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setWindowTitle("设置中心")
        self.resize(560, 240)

        self.edits = {}
        form = QFormLayout()

        labels = {
            "install_dir": "安装目录",
            "download_dir": "临时下载目录",
            "archive_dir": "用户数据冻结归档目录",
        }
        for key in DIR_KEYS:
            edit = QLineEdit(self.cfg.get(key, ""))
            btn = QPushButton("浏览…")
            btn.clicked.connect(lambda _=False, e=edit: self._browse(e))
            from PySide6.QtWidgets import QHBoxLayout, QWidget
            holder = QWidget()
            h = QHBoxLayout(holder)
            h.setContentsMargins(0, 0, 0, 0)
            h.addWidget(edit)
            h.addWidget(btn)
            form.addRow(labels[key], holder)
            self.edits[key] = edit

        self.tier = QComboBox()
        for n in TIER_OPTIONS:
            self.tier.addItem(f"{n} 个", n)
        cur_tier = int(self.cfg.get("tier", 30))
        idx = self.tier.findData(cur_tier)
        self.tier.setCurrentIndex(idx if idx >= 0 else 0)
        form.addRow("内置应用数量", self.tier)

        self.concurrency = QSpinBox()
        self.concurrency.setRange(1, 10)
        self.concurrency.setValue(int(self.cfg.get("concurrency", 3)))
        form.addRow("下载并发数", self.concurrency)

        self.manifest = QLineEdit(self.cfg.get("manifest_url", ""))
        form.addRow("更新源地址", self.manifest)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

    def _browse(self, edit: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, "选择目录", edit.text())
        if path:
            edit.setText(path)

    def _on_save(self):
        # 目录变更：逐个询问是否迁移
        for key in DIR_KEYS:
            old = self.cfg.get(key, "")
            new = self.edits[key].text().strip()
            if not new:
                QMessageBox.warning(self, "设置", f"{key} 不能为空。")
                return
            if new != old and os.path.exists(old):
                ret = QMessageBox.question(
                    self, "目录变更",
                    f"目录已从\n{old}\n改为\n{new}\n\n是否将已有文件迁移到新目录？",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes,
                )
                if ret == QMessageBox.Yes:
                    result = self.cfg.migrate_directory(key, new)
                    if result["error"]:
                        QMessageBox.critical(self, "迁移失败", result["error"])
                        return
                    logger.info("目录 %s 已迁移 %d 个文件到 %s", key, result["files"], new)
                else:
                    self.cfg.set(key, new)
            else:
                self.cfg.set(key, new)

        old_tier = int(self.cfg.get("tier", 30))
        new_tier = int(self.tier.currentData())
        self.cfg.set("tier", new_tier)
        self.cfg.set("concurrency", self.concurrency.value())
        self.cfg.set("manifest_url", self.manifest.text().strip())
        self.cfg.save()
        if new_tier != old_tier:
            logger.info("内置应用数量由 %d 调整为 %d", old_tier, new_tier)
            QMessageBox.information(
                self, "内置应用数量已更新",
                f"内置应用数量已调整为 {new_tier} 个。\n"
                f"新增显示的工具可按需下载到临时下载目录。")
        logger.info("设置已保存")
        self.accept()
