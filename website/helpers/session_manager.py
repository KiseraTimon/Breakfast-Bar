from flask import session
import time
from utils import errhandler

from . import generator

class SessionManager:

    @staticmethod
    def update_session(
        email: str = None
    ) -> bool:
        # Constants
        CODE_LENGTH = 8
        CODE_VALIDITY = 300

        try:
            code = generator(int(CODE_LENGTH))
            expiry = time.time() + int(CODE_VALIDITY)

            session['verification'] = {
                "code": code,
                "expiry": expiry,
                "email": email,
                "createdAt": time.time()
            }

        except Exception as e:
            errhandler(e, log="session_manager", path="helpers")

            return False

        else:
            return True
