from database import db

from . import ValidationResult, FormValidator

from utils import errhandler

class SigninValidator(FormValidator):
    """Signin event options"""

    # Validator Function
    def validate(self) -> ValidationResult:
        # Method Check
        r = self.validate_method()
        if r:
            return r

        # Required Fields Check
        r = self.require_fields(["identifier", "key"])
        if r:
            return r

        # Extracting Form Data
        identifier = self.form.get("identifier", None)
        password = self.form.get("key", None)

        # Identity Lookup
        user = self.identity_lookup(identifier)
        if isinstance(user, ValidationResult):
            return ValidationResult.fail("An error occurred retrieving your account", code="db_error")

        if user is None:
            return ValidationResult.fail("Invalid credentials", code="missing_account")

        # Password Check
        if not (user and user.check_password(password)):
            return ValidationResult.fail("Invalid signin details", code="invalid_credentials")

        # Checking Account Activity Status
        # if not getattr(user, "is_verified", False):
        #     return ValidationResult.fail("Inactive account. Contact support", code="inactive_account")

        # Updating Last Login
        try:
            user.update_last_login()
        except Exception as e:
            errhandler(e, log="signin-validator", path="auth")

            return ValidationResult.fail("An error occurred authenticating you", code="db_error")
        else:
            return ValidationResult.ok(
                obj=user,
                data={
                    "identifier": identifier
                },
                code="signin_ok"
            )

