from . import FormValidator, ValidationResult


class SignupValidator(FormValidator):
    """Signup events options"""

    # Validator Function
    def validate(self) -> ValidationResult:
        r = self.validate_method()
        if r:
            return r

        # Validating Required Fields
        r = self.require_fields([
            "first_name", "last_name", "email", "key", "key_check"
        ])
        if r:
            return r

        # Email Format Check
        r = self.email_format("email")
        if r:
            return r

        # Reading Form Data
        first_name = (self.form.get("first_name") or "").strip()
        last_name = (self.form.get("last_name") or "").strip()
        email = (self.form.get("email") or "").strip()
        key = self.form.get("key", None).strip()
        key_check = self.form.get("key_check", None).strip()

        # Length Checks
        if len(key) < self.MIN_PASS_LENGTH:
            return ValidationResult.fail(f"Password must be at least {self.MIN_PASS_LENGTH} characters", code="weak_password")

        if len(first_name) < self.MIN_NAME_LENGTH or len(last_name) < self.MIN_NAME_LENGTH:
            return ValidationResult.fail(f"First and last names must be at least {self.MIN_NAME_LENGTH} characters", code="short_name")

        # Password Match Checks
        if key != key_check:
            return ValidationResult.fail("Passwords do not match", code="password_mismatch")

        # Identity Lookup
        user = self.identity_lookup(email)
        if isinstance(user, ValidationResult):
            return user

        # Updating Last Login
        try:
            user.update_last_login()
        except Exception as e:
            errhandler(e, log="signup-validator", path="auth")

            return ValidationResult.fail("An error occurred authenticating you. Contact support", code="db_error")
        else:
            # Payload
            payload = {
                "fName": fName,
                "lName": lName,
                "uName": uName,
                "email": email,
                "password": password,
                "role": "user"
            }

            return ValidationResult.ok(
                obj=payload,
                data=payload,
                code="signup_ok"
            )