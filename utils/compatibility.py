from .terminal_messenger import TerminalMessenger
from .time_utils import TimeUtils
from .error_extractor import ErrorExtractor
from .error_handler import ErrorHandler
from .sys_logger import SystemLogger
from .mail_manager import MailManager
from .file_zipper import FileZipper
from .filename_manager import FilenameManager
from .filing_manager import FilingManager


def message(text): return TerminalMessenger.message(text)
def timestp(): return TimeUtils.timestp()
def error(e): return ErrorExtractor.error(e)
def errhandler(e, log, **k): return ErrorHandler.errhandler(e, log, **k)
def syshandler(m, log, **k): return SystemLogger.syshandler(m, log, **k)
def mailer(r, s, **k): return MailManager.mailer(r, s, **k)
def zipfilehandler(f, o, **k): return FileZipper.zipfilehandler(f, o, **k)
def stripPrefix(f): return FilenameManager.stripPrefix(f)
def cleanFilename(f): return FilenameManager.cleanFilename(f)
def filehandler(**k): return FilingManager.filehandler(**k)
