"""冻结压缩模块：把工具的用户数据目录打包为 zip 归档。"""
import os
import shutil
import zipfile
from datetime import datetime
from typing import Optional

from .logger import get_logger

logger = get_logger(__name__)


def freeze_userdata(tool_id: str, userdata_dir: str, archive_dir: str) -> Optional[str]:
    """将指定工具的用户数据目录冻结压缩到归档目录。

    返回归档文件路径；用户数据为空或不存在时返回 None。
    """
    if not os.path.isdir(userdata_dir):
        logger.info("工具 %s 无用户数据，跳过冻结", tool_id)
        return None
    if not os.listdir(userdata_dir):
        logger.info("工具 %s 用户数据为空，跳过冻结", tool_id)
        return None

    os.makedirs(archive_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = os.path.join(archive_dir, f"{tool_id}_userdata_{stamp}.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _dirs, files in os.walk(userdata_dir):
            for name in files:
                full = os.path.join(root, name)
                arc = os.path.relpath(full, userdata_dir)
                zf.write(full, arc)

    logger.info("工具 %s 用户数据已冻结：%s", tool_id, zip_path)
    return zip_path


def remove_from_download_dir(tool_id: str, download_dir: str) -> bool:
    """将工具从临时下载目录中删除。"""
    target = os.path.join(download_dir, tool_id)
    if not os.path.exists(target):
        return False
    shutil.rmtree(target, ignore_errors=True)
    logger.info("工具 %s 已从临时下载目录删除", tool_id)
    return True
