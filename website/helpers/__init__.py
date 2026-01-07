
from .code_generator import CodeGenerator
from .session_manager import SessionManager
from .mail_manager import MailManager

# Backward Compatibility
def generator(l): return CodeGenerator.generator(l)
def manager(s, e): return SessionManager.update_session(s, e)
def mailer(s, r, c, m): return MailManager.mail_options(s, r, c, m)


__all__ = [
    "generator",
    "manager",
    "mailer"
]