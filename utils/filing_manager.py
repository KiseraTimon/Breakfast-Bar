import os
from datetime import datetime

from .filename_manager import FilenameManager
from .error_handler import ErrorHandler
from .sys_logger import SystemLogger


class FilingManager:
    @staticmethod
    def filehandler(**kwargs):
        item = kwargs.get("item")
        itemType = kwargs.get("type", "image")
        path = kwargs.get("path", "uploads")
        subPath = kwargs.get("subPath", "undefined")
        operation = kwargs.get("operation")

        DEFAULT_ITEM_PATH = os.path.join(
            "website", "static", "uploads", "item-not-found.png"
        ).replace("\\", "/")

        if not item:
            return DEFAULT_ITEM_PATH

        if itemType == "image":
            upload_dir = os.path.join("website", "static", path, "images", subPath)
            allowed = {"png", "jpg", "jpeg", "gif"}

        elif itemType == "file":
            upload_dir = os.path.join("website", "static", path, "files", subPath)
            allowed = {
                "png", "jpg", "jpeg", "gif",
                "zip", "pdf", "csv", "7zip",
                "rar", "docx", "xlsx"
            }

        else:
            SystemLogger.syshandler(
                f"Unknown itemType '{itemType}'",
                log="filehandler",
                path="utils"
            )
            return DEFAULT_ITEM_PATH

        if operation is None or operation == "add":
            try:
                if not getattr(item, "filename", ""):
                    return DEFAULT_ITEM_PATH

                if "." not in item.filename:
                    return DEFAULT_ITEM_PATH

                ext = item.filename.rsplit(".", 1)[1].lower()
                if ext not in allowed:
                    return DEFAULT_ITEM_PATH

                filename = FilenameManager.cleanFilename(item.filename)
                ts = datetime.now().strftime("%Y%m%d%H%M%S")
                filename = f"{ts}_{filename}"

                save_path = os.path.join(upload_dir, filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)

                item.save(save_path)
                return save_path.replace("\\", "/")

            except Exception as e:
                ErrorHandler.errhandler(e, log="filehandler", path="utils")
                return DEFAULT_ITEM_PATH

        return DEFAULT_ITEM_PATH
