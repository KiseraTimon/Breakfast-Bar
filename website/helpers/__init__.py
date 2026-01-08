
from .code_generator import CodeGenerator
from .session_manager import SessionManager
from .mail_manager import MailManager

# Backward Compatibility
def generator(l): return CodeGenerator.generator(l)
def manager(s=None, e=None): return SessionManager.update_session(s, e)
def mailer(s=None, r=None, c=None, m=None): return MailManager.mail_options(s, r, c, m)


__all__ = [
    "generator",
    "manager",
    "mailer"
]