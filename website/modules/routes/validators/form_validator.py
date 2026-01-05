from typing import Any, Dict, List, Optional, Sequence

from sqlalchemy import select, or_
from database import db
from website.models import User, Customer

from . import ValidationResult

import re
from utils import errhandler


class FormValidator:
    """Base class for validators"""

    # Constants
    METHODS_ALLOWED = ("POST",)
    MIN_PASS_LENGTH = 8
    MIN_NAME_LENGTH = 3
    MIN_PHONE_LENGTH = 13

    # Constructor
    def __init__(
        self,
        form: Dict[str, Any],   # Form Data
        method: str             # Access Method
    ):
        self.form = form or {}
        self.method = (method or "GET").upper()

    # Validating Request Method
    def validate_method(self) -> Optional[ValidationResult]:
        if self.method not in self.METHODS_ALLOWED:
            return ValidationResult.fail("Invalid request method", code="invalid_method")

        return None

    # Validating Required Fields
    def require_fields(self, fields: Sequence[str]) -> Optional[ValidationResult]:
        missing = [f for f in fields if not self.form.get(f)]

        if missing:
            return ValidationResult.fail(f"Missing required fields: {', '.join(missing)}", code="missing_fields", errors=missing)

        return None

    # Validating Email Format
    def email_format(self, field: str = "email") -> Optional[ValidationResult]:
        email = (self.form.get(field) or field)

        if not email:
            return ValidationResult.fail("Invalid email format", code="invalid_email")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return ValidationResult.fail("Invalid email format", code="invalid_email")

        return None

    # Identity Lookup
    def identity_lookup(self, identifier: str) -> Optional[ValidationResult]:
        try:
            user = db.session.execute(
                select(User).where(User.email == identifier)
            ).scalar_one_or_none()

            if user:
                return user

            customer = db.session.execute(
                select(Customer).where(Customer.email == identifier)
            ).scalar_one_or_none()

            return customer

        except Exception as e:
            errhandler(e, log="signup-validator", path="auth")

            return ValidationResult.fail("Lookup Error", code="db_error")

    # Target Resolution Helper
    def resolve_target(self, current_user, session_store: dict = None) -> Optional[ValidationResult]:

        target = None
        session_data = (session_store or {}).get("verification", {}) if session_store else None

        try:
            # Current User preference
            if current_user is not None:
                target = current_user

            else:
                # User from session preference
                if not session_data:
                    return ValidationResult.fail("Missing validation credentials", code="missing_session")

                found = self.identity_lookup(session_data.get("email", None))
                if (isinstance(found, ValidationResult) and not found.success):
                    return found

                target = found

        except Exception as e:
            errhandler(e, log="verify-validator", path="auth")

            return ValidationResult.fail("An error occurred looking up your account. Contact Support", code="lookup_error")

        else:
            # Checking Target Mismatch
            if (session_data.get("email", None)) and (getattr(target, "email", None) != session_data.get("email", None)):
                return ValidationResult.fail("Your account details are inaccurate. Contact support", code="account_mismatch")

            return target
