from typing import Dict
from utils import errhandler
from . import FormValidator, ValidationResult

class ResetValidator(FormValidator):
    """Password reset event options"""

    # Account Resolution
    def mail_lookup(
        self,
        current_user = None,
        session_store: dict=None
    ) -> ValidationResult:
        # Access Method Check
        r = self.validate_method()
        if r:
            return r

        # Email Format Check
        r = self.email_format()
        if r:
            return r

        # Reading Form Data
        email = str(self.form.get("email", "")).strip().lower()

        # Resolving Target
        user = self.resolve_target(
            current_user=current_user,
            session_store=session_store
        )

        if isinstance(user, ValidationResult):
            return ValidationResult.fail("An error occurred looking up your account. Contact support", code="lookup_miss")

        return ValidationResult.ok(
            obj=user,
            data = {
                "token_ok": True,
                "email": getattr(user, "email", None)
            },
            code = "reset_mail_ok"
        )

    def validate_key(
        self,
        current_user = None,
        session_store: dict = None
    ) -> ValidationResult:
        # Access Method Check
        r = self.validate_method()
        if r:
            return r

        # Extracting Code
        code = (self.form.get("code", "") or "").strip()

        if not code:
            return ValidationResult.fail("Invalid reset code", code="invalid_code")

        # Resolving Target
        user = self.resolve_target(
            current_user=current_user,
            session_store=session_store
        )

        if isinstance(user, ValidationResult):
            return ValidationResult.fail("An error occurred looking up your account. Contact support", code="lookup_miss")

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

        return ValidationResult.ok(
            obj=target,
            data={
                "token_ok": True,
                "email": getattr(target, "email", None)
            },
            code="reset_key_ok"
        )

    def validate(
        self,
        current_user=None,
        session_store: dict = None
    ) -> ValidationResult:
        # Access Method Check
        r = self.validate_method()
        if r: return r

        # Extracting Form Data
        key = self.form.get("key")
        key_check = self.form.get("key_check")

        # Missing Passwords Check
        if not (password and password_check):
            return ValidationResult.fail("Missing required fields", code="missing_fields")

        # Mismatch Check
        if key != key_check:
            return ValidationResult.fail("Passwords do not match", code="password_mismatch")

        # Length Checks
        if len(key) < self.MIN_PASS_LENGTH:
            return ValidationResult.fail(f"Password must be at least {self.MIN_PASS_LENGTH} characters", code="weak_password")

        # Resolving Target
        user = self.resolve_target(
            current_user=current_user,
            session_store=session_store
        )

        if isinstance(user, ValidationResult):
            return ValidationResult.fail("An error occurred looking up your account. Contact support", code="lookup_miss")

        # Password Verification
        try:
            if hasattr(target, "check_password") and target.check_password(password):
                # Fail Validation
                return ValidationResult.fail("New password must be different from the old password", code="same_password")

        # Handling Exceptions
        except Exception as e:
            # Logging Error
            errhandler(e, log="reset-validator", path="auth")

            # Fail Validation
            return ValidationResult.fail("An error occurred validating your password. Try again later", code="password_check_failed")

        # Loading Client to Mail
        # toMail = getattr(target, "email", None)

        try:
            # Hashing & Updating Password
            user.set_password(key)

        # Handling Exceptions
        except Exception as e:
            # Logging Error
            errhandler(e, log="reset-validator", path="auth")

            # Fail Validation
            return ValidationResult.fail("An error occurred processing your password reset request. Contact support", code="reset_failed")

        # Mail User
        # _ = mail_manager(recipient=toMail, mode=2)

        # Pass Validation
        return ValidationResult.ok(
            obj=target,
            data={
                "changed": True,
                "email": toMail
            },
            code="password_updated_ok"
        )
