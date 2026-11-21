"""计算机人员专业工具箱 Beta v0.3 —— 程序入口。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from core.logger import get_logger


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("计算机人员专业工具箱")
    app.setOrganizationName("ToolboxAlpha")
    logger = get_logger("toolbox.main")
    logger.info("=== 计算机人员专业工具箱 Beta v0.3 启动 ===")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
