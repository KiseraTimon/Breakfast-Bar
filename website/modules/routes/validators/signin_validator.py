from utils.compatibility import errhandler
from . import FormValidator, ValidationResult

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
            return user

        # Password Check
        if not (user and user.check_passsword(password)):
            return ValidationResult.fail("Invalid signin details", code="invalid_credentials")

        # Checking Account Activity Status
        if not getattr(user, "is_active", True):
            return ValidationResult.fail("Inactive account. Contact support", code="inactive_account")

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

