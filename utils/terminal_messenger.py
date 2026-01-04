import logging
from .log_config import logger, fileFormat


class TerminalMessenger:
    @staticmethod
    def message(text):
        console = logging.StreamHandler()
        console.setFormatter(fileFormat)
        logger.addHandler(console)
        try:
            logger.info(text)
        finally:
            logger.removeHandler(console)
