from typing import Dict, List, Optional
import re


class AuthValidator:
    """
    Single validator for ALL auth operations.
    ONLY validates format - NO database access!
    """

    # Constants
    MIN_PASSWORD_LENGTH = 8
    MIN_NAME_LENGTH = 3
    MIN_PHONE_LENGTH = 13

    @staticmethod
    def validate_email(email: str) -> Optional[str]:
        """
        Validate email format.
        Returns error message if invalid, None if valid.
        """
        if not email:
            return "Email is required"

        email = email.strip().lower()

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return "Invalid email format"

        return None

    @staticmethod
    def validate_phone(phone: str) -> Optional[str]:
        """
        Validate phone format.
        Returns error message if invalid, None if valid.
        """
        if not phone:
            return "Phone number is required"

        phone = phone.strip()

        if len(phone) < AuthValidator.MIN_PHONE_LENGTH:
            return f"Phone number must be at least {AuthValidator.MIN_PHONE_LENGTH} characters"

        return None

    @staticmethod
    def validate_password(password: str) -> Optional[str]:
        """
        Validate password strength.
        Returns error message if invalid, None if valid.
        """
        if not password:
            return "Password is required"

        if len(password) < AuthValidator.MIN_PASSWORD_LENGTH:
            return f"Password must be at least {AuthValidator.MIN_PASSWORD_LENGTH} characters"

        return None

    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> Optional[str]:
        """
        Validate name length.
        Returns error message if invalid, None if valid.
        """
        if not name:
            return f"{field_name} is required"

        name = name.strip()

        if len(name) < AuthValidator.MIN_NAME_LENGTH:
            return f"{field_name} must be at least {AuthValidator.MIN_NAME_LENGTH} characters"

        return None

    @staticmethod
    def validate_passwords_match(password: str, password_check: str) -> Optional[str]:
        """
        Validate passwords match.
        Returns error message if don't match, None if valid.
        """
        if password != password_check:
            return "Passwords do not match"

        return None

    @staticmethod
    def validate_required_fields(data: Dict, required: List[str]) -> Optional[str]:
        """
        Validate required fields are present.
        Returns error message with missing fields, None if all present.
        """
        missing = [field for field in required if not data.get(field)]

        if missing:
            return f"Missing required fields: {', '.join(missing)}"

        return None

    @staticmethod
    def validate_code(code: str) -> Optional[str]:
        """
        Validate verification/reset code format.
        Returns error message if invalid, None if valid.
        """
        if not code:
            return "Verification code is required"

        code = code.strip()

        if len(code) < 4:  # Minimum 4-digit codes
            return "Invalid verification code"

        return None

    # Combined Validation Methods

    @classmethod
    def validate_signin_form(cls, form: Dict) -> Optional[str]:
        """
        Validate signin form.
        Returns error message if invalid, None if valid.
        """
        # Required fields
        error = cls.validate_required_fields(form, ["identifier", "key"])
        if error:
            return error

        identifier = form.get("identifier", "").strip()
        password = form.get("key", "")

        # Validate identifier (email or phone)
        if '@' in identifier:
            error = cls.validate_email(identifier)
        else:
            error = cls.validate_phone(identifier)

        if error:
            return error

        # Validate password
        error = cls.validate_password(password)
        if error:
            return error

        return None

    @classmethod
    def validate_signup_form(cls, form: Dict) -> Optional[str]:
        """
        Validate signup form.
        Returns error message if invalid, None if valid.
        """
        # Required fields
        error = cls.validate_required_fields(
            form,
            ["first_name", "last_name", "email", "phone", "key", "key_check"]
        )
        if error:
            return error

        # Validate names
        error = cls.validate_name(form.get("first_name", ""), "First name")
        if error:
            return error

        error = cls.validate_name(form.get("last_name", ""), "Last name")
        if error:
            return error

        # Validate email
        error = cls.validate_email(form.get("email", ""))
        if error:
            return error

        # Validate phone
        error = cls.validate_phone(form.get("phone", ""))
        if error:
            return error

        # Validate password
        error = cls.validate_password(form.get("key", ""))
        if error:
            return error

        # Validate passwords match
        error = cls.validate_passwords_match(
            form.get("key", ""),
            form.get("key_check", "")
        )
        if error:
            return error

        return None

    @classmethod
    def validate_verify_form(cls, form: Dict) -> Optional[str]:
        """
        Validate verification form.
        Returns error message if invalid, None if valid.
        """
        error = cls.validate_required_fields(form, ["code"])
        if error:
            return error

        error = cls.validate_code(form.get("code", ""))
        if error:
            return error

        return None

    @classmethod
    def validate_reset_email_form(cls, form: Dict) -> Optional[str]:
        """
        Validate password reset email request form.
        Returns error message if invalid, None if valid.
        """
        error = cls.validate_required_fields(form, ["email"])
        if error:
            return error

        error = cls.validate_email(form.get("email", ""))
        if error:
            return error

        return None

    @classmethod
    def validate_reset_code_form(cls, form: Dict) -> Optional[str]:
        """
        Validate password reset code form.
        Returns error message if invalid, None if valid.
        """
        error = cls.validate_required_fields(form, ["code"])
        if error:
            return error

        error = cls.validate_code(form.get("code", ""))
        if error:
            return error

        return None

    @classmethod
    def validate_reset_password_form(cls, form: Dict) -> Optional[str]:
        """
        Validate password reset form.
        Returns error message if invalid, None if valid.
        """
        error = cls.validate_required_fields(form, ["key", "key_check"])
        if error:
            return error

        error = cls.validate_password(form.get("key", ""))
        if error:
            return error

        error = cls.validate_passwords_match(
            form.get("key", ""),
            form.get("key_check", "")
        )
        if error:
            return error

        return None