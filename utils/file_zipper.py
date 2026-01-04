import os
import zipfile
from datetime import datetime


class FileZipper:
    @staticmethod
    def zipfilehandler(filePath, outputDir, **kwargs):
        os.makedirs(outputDir, exist_ok=True)

        client = kwargs.get("client")
        ts = datetime.now().strftime("%Y%m%d%H%M%S")

        zip_name = f"{ts}_{client}_.zip" if client else f"{ts}_AuditFile.zip"
        zip_path = os.path.join(outputDir, zip_name)

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for fp in filePath:
                if os.path.exists(fp):
                    zipf.write(fp, os.path.basename(fp))

        return zip_name, zip_path
