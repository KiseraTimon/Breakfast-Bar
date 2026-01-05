from utils import mailer, errhandler
from typing import Optional, Dict, Union

from flask import session

# Mail Modes
ModeType = Union[int, str, None]

class MailManager:

    @staticmethod
    def mail_options(
        recipient: str = session.get("verification", {}).get("email", None),
        code: str = session.get("verification", {}).get("code", None),
        mode: ModeType = None
    ) -> bool:
        sent: bool = False

        try:
            if mode in (0, 1) and not code:
                return False

            if mode == 0:
                subject = "Breakfast Bar | Verification Code"
                body = f"""
                Hello,

                Welcome to the Breakfast Bar

                Your verification code to finalize authentication is:
                {code}

                Your verification code will expire in 5 minutes, so be sure to verify your account promptly

                Regards,
                """

            elif mode == 1:
                # Mailing Format
                subject="Breakfast Bar | Password Reset Code"
                body = f"""
                Hello,

                Welcome to the Breakfast Bar

                A password reset has been triggered for your account.
                Your reset code to continue with the process is:
                {code}

                Your reset code will expire in 5 minutes, so be sure to reset your password promptly.

                Regards,
                """

            elif mode == 2:
                subject="Breakfast Bar | Password Change Notice"
                body = f"""
                Hello,

                Welcome to the Breakfast Bar

                Your account password has been successfully changed.
                Be careful who you give access to your account as they can then view sensitive information related to you.

                If by chance you did not initiate this process. Contact us here immediately:

                +254 799 999999

                Regards,
                """

            else:
                return False

            sent = mailer(
                recipient=recipient,
                subject=subject,
                body=body
            )

            return bool(sent)

        except Exception as e:
            errhandler(e, log="mail-manager", path="helpers")

            return False