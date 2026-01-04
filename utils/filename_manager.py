import os
import re


class FilenameManager:
    @staticmethod
    def stripPrefix(filename):
        return "_".join(filename.split("_")[1:]) if "_" in filename else filename

    @staticmethod
    def cleanFilename(filename):
        filename = os.path.basename(filename)
        return re.sub(r"[^\w\-.]", "_", filename)
