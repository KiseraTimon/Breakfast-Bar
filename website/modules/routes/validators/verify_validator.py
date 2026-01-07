from utils import errhandler
from . import FormValidator, ValidationResult
import time
from website.helpers import manager, mailer

class VerifyValidator(FormValidator):
    """Verification event options"""

    # Validation Function
    def validate(
        self,
        current_user = None,
        session_store: dict = None
    ) -> ValidationResult:
        # Validating Access Method
        r = self.validate_method()
        if r:
            return r

        # Extracting Verification Code
        code = self.form.get("code", "").strip()

        if not code:
            return ValidationResult.fail("Missing verification code", code="missing_code")

        user = self.resolve_target(
            current_user=current_user,
            session_store=session_store
        )

        if isinstance(user, ValidationResult):
            return ValidationResult.fail("An error occurred resolving your account", code="lookup_miss")

        # Checking for Already Activated Accounts
        if getattr(user, "is_verified", False):
            return ValidationResult.fail("Your account is already verified", code="already_verified")

        # Extracting Verification Session Attributes
        session_data = (session_store or {}).get("verification", {})
        if session_data is None:
            return ValidationResult.fail("Missing verification data", code="missing_verification_data")

        session_code = session_data.get("code")
        session_code_expiry = session_data.get("expiry")
        now = time.now()

        # Code Mismatch Check
        if (not session_code) and (session_code != code):
            return ValidationResult.fail("Invalid verification code", code="invalid_code")

        # Expired Code Check
        if (session_code_expiry) and (now > float(session_code_expiry)):
            return ValidationResult.fail("The verification code is expired", code="expired_code")

        # Activating User Account
        return ValidationResult.ok(
            obj=target,
            data={
                "email": getattr(user, "email", None)
            },
            code="verified_account"
        )

    # Account Update Function
    def account_update(
        instance: object = None
    ) -> ValidationResult:
        if not instance:
            return ValidationResult.fail("Your account could not be verified. Contact support", code="user_missing")

        try:
            instance.update_status(True)

        except Exception as e:
            errhandler(e, log="verify-validator", path="auth")

            return ValidationResult.fail("Your account could not be verified. Contact support", code="db_error")

        else:
            return ValidationResult.ok(
                obj=instance,
                data={
                    "verified": getattr(instance, "is_verified", False)
                },
                code="activated_account"
            )

    # Resend Code
    def resend_code(
        self,
        current_user = None,
        session_store: dict = None
    ) -> bool:
        # Validating Access Method
        r = self.validate_method()
        if r:
            return r

        user = self.resolve_target(
            current_user=current_user,
            session_store=session_store
        )

        if isinstance(user, ValidationResult):
            return ValidationResult.fail("An error occurred resolving your account", code="lookup_miss")

        # Checking for Already Activated Accounts
        if getattr(user, "is_verified", False):
            return ValidationResult.fail("Your account is already verified", code="already_verified")

        # Helpers
        try:
            manager(
                s=session_store,
                e=user.email
            )
            mailer(
                s=session_store,
                r=user.email,
                m=0
            )

        except Exception as e:
            errhandler(e, log="verify-validator", path="auth")

            return False

        else:
            mailer(
                r=user.email,
                m=1
            )

            return True
