from typing import Optional, Union, Dict
import time

from website.models import User, Customer
from website.repositories import UserRepository, CustomerRepository

from website.validators import AuthValidator, ValidationResult
from website.helpers import manager, mailer

from utils import errhandler
from database import db


class AuthService:
    """
    Central service for ALL authentication operations.
    Handles business logic, database operations, and session management.
    """

    def __init__(
        self,
        user_repo: UserRepository = None,
        customer_repo: CustomerRepository = None
    ):
        self.user_repo = user_repo or UserRepository()
        self.customer_repo = customer_repo or CustomerRepository()

    # Identity Lookup
    def find_identity(self, identifier: str) -> Optional[Union[User, Customer]]:
        """
        Find user or customer by email or phone.
        Returns User or Customer if found, None otherwise.
        """
        try:
            # Determine if email or phone
            if '@' in identifier:
                # Try User first
                user = self.user_repo.find_by_email(identifier)
                if user:
                    return user
                # Then Customer
                return self.customer_repo.find_by_email(identifier)
            else:
                # Try User first
                user = self.user_repo.find_by_phone(identifier)
                if user:
                    return user
                # Then Customer
                return self.customer_repo.find_by_phone(identifier)
        except Exception as e:
            errhandler(e, log="auth_service", path="services")
            return None

    def identity_exists(self, email: str = None, phone: str = None) -> bool:
        """
        Check if identity (email or phone) already exists.
        """
        try:
            if email:
                if self.user_repo.find_by_email(email):
                    return True
                if self.customer_repo.find_by_email(email):
                    return True

            if phone:
                if self.user_repo.find_by_phone(phone):
                    return True
                if self.customer_repo.find_by_phone(phone):
                    return True

            return False
        except Exception as e:
            errhandler(e, log="auth_service", path="services")
            return True  # Fail safe - assume exists to prevent duplicates

    def resolve_user_from_session(self, session_store: dict) -> Optional[Union[User, Customer]]:
        """
        Resolve user from session verification data.
        """
        try:
            session_data = session_store.get("verification", {})
            email = session_data.get("email")

            if not email:
                return None

            return self.find_identity(email)
        except Exception as e:
            errhandler(e, log="auth_service", path="services")
            return None

    # Signin
    def signin(self, identifier: str, password: str) -> ValidationResult:
        """
        Authenticate user with identifier (email/phone) and password.
        Returns ValidationResult with user object if successful.
        """
        try:
            # Validate format first
            error = AuthValidator.validate_signin_form({
                "identifier": identifier,
                "key": password
            })
            if error:
                return ValidationResult.fail(error, code="validation_error")

            # Find user
            user = self.find_identity(identifier)
            if not user:
                return ValidationResult.fail(
                    "Invalid credentials",
                    code="invalid_credentials"
                )

            # Check password
            if not user.check_password(password):
                return ValidationResult.fail(
                    "Invalid credentials",
                    code="invalid_credentials"
                )

            # Update last login
            user.update_last_login()
            db.session.commit()

            return ValidationResult.ok(
                message="Sign in successful",
                code="signin_success",
                obj=user
            )

        except Exception as e:
            db.session.rollback()
            errhandler(e, log="auth_service", path="services")
            return ValidationResult.fail(
                "An error occurred during sign in",
                code="signin_error"
            )

    # Signup
    def signup(self, form_data: Dict) -> ValidationResult:
        """
        Register a new user.
        Returns ValidationResult with user object if successful.
        """
        try:
            # Validate format
            error = AuthValidator.validate_signup_form(form_data)
            if error:
                return ValidationResult.fail(error, code="validation_error")

            # Extract data
            first_name = form_data.get("first_name", "").strip()
            last_name = form_data.get("last_name", "").strip()
            email = form_data.get("email", "").strip().lower()
            phone = form_data.get("phone", "").strip()
            password = form_data.get("key", "")

            # Check if identity already exists
            if self.identity_exists(email=email):
                return ValidationResult.fail(
                    "Email address is already registered",
                    code="email_exists"
                )

            if self.identity_exists(phone=phone):
                return ValidationResult.fail(
                    "Phone number is already registered",
                    code="phone_exists"
                )

            # Create user
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone
            )
            user.set_password(password)
            user.update_status(active=False)  # Not active until verified
            user.update_last_login()

            # Save to database
            self.user_repo.create(user)

            return ValidationResult.ok(
                message="Account created successfully",
                code="signup_success",
                obj=user
            )

        except Exception as e:
            db.session.rollback()
            errhandler(e, log="auth_service", path="services")
            return ValidationResult.fail(
                "An error occurred creating your account",
                code="signup_error"
            )

    # Verification
    def verify_code(
        self,
        code: str,
        current_user: Optional[User],
        session_store: dict
    ) -> ValidationResult:
        """
        Verify email verification code.
        Returns ValidationResult with user object if successful.
        """
        try:
            # Validate code format
            error = AuthValidator.validate_verify_form({"code": code})
            if error:
                return ValidationResult.fail(error, code="validation_error")

            # Resolve user
            if current_user and current_user.is_authenticated:
                user = current_user
            else:
                user = self.resolve_user_from_session(session_store)

            if not user:
                return ValidationResult.fail(
                    "User not found",
                    code="user_not_found"
                )

            # Check if already verified
            if getattr(user, "is_verified", False):
                return ValidationResult.fail(
                    "Account is already verified",
                    code="already_verified"
                )

            # Get session data
            session_data = session_store.get("verification", {})
            if not session_data:
                return ValidationResult.fail(
                    "Verification session expired",
                    code="session_expired"
                )

            session_code = session_data.get("code")
            session_expiry = session_data.get("expiry")

            # Validate code
            if not session_code or session_code != code.strip():
                return ValidationResult.fail(
                    "Invalid verification code",
                    code="invalid_code"
                )

            # Check expiry
            if session_expiry and time.time() > float(session_expiry):
                return ValidationResult.fail(
                    "Verification code has expired",
                    code="code_expired"
                )

            # Mark as verified
            user.is_verified = True
            user.update_status(active=True)
            db.session.commit()

            return ValidationResult.ok(
                message="Account verified successfully",
                code="verify_success",
                obj=user
            )

        except Exception as e:
            db.session.rollback()
            errhandler(e, log="auth_service", path="services")
            return ValidationResult.fail(
                "An error occurred during verification",
                code="verify_error"
            )

    def resend_verification_code(
        self,
        current_user: Optional[User],
        session_store: dict
    ) -> ValidationResult:
        """
        Resend verification code.
        """
        try:
            # Resolve user
            if current_user and current_user.is_authenticated:
                user = current_user
            else:
                user = self.resolve_user_from_session(session_store)

            if not user:
                return ValidationResult.fail(
                    "User not found",
                    code="user_not_found"
                )

            # Check if already verified
            if getattr(user, "is_verified", False):
                return ValidationResult.fail(
                    "Account is already verified",
                    code="already_verified"
                )

            # Generate and send new code
            session_man = manager(s=session_store, e=user.email)
            send_mail = mailer(s=session_store, r=user.email, c=None, m=0)

            if not (session_man and send_mail):
                return ValidationResult.fail(
                    "A verification code could not be sent to your email",
                    code="verification_failure"
                )

            return ValidationResult.ok(
                message="Verification code sent",
                code="code_sent"
            )

        except Exception as e:
            errhandler(e, log="auth_service", path="services")
            return ValidationResult.fail(
                "An error occurred sending verification code",
                code="resend_error"
            )

    # Password Reset
    def request_password_reset(self, email: str, session_store: dict) -> ValidationResult:
        """
        Initiate password reset process.
        """
        try:
            # Validate email format
            error = AuthValidator.validate_reset_email_form({"email": email})
            if error:
                return ValidationResult.fail(error, code="validation_error")

            # Find user
            user = self.find_identity(email)
            if not user:
                # Don't reveal if email exists or not (security)
                return ValidationResult.ok(
                    message="If the email exists, a reset code will be sent",
                    code="reset_initiated"
                )

            # Generate and send reset code
            session_man = manager(s=session_store, e=user.email)
            send_mail = mailer(s=session_store, r=user.email, c=None, m=0)

            if not (session_man and send_mail):
                return ValidationResult.fail(
                    "A verification code could not be sent to your email",
                    code="verification_failure"
                )

            return ValidationResult.ok(
                message="Reset code sent to your email",
                code="reset_code_sent"
            )

        except Exception as e:
            errhandler(e, log="auth_service", path="services")
            return ValidationResult.fail(
                "An error occurred processing your request",
                code="reset_request_error"
            )

    def verify_reset_code(
        self,
        code: str,
        session_store: dict
    ) -> ValidationResult:
        """
        Verify password reset code.
        """
        try:
            # Validate code format
            error = AuthValidator.validate_reset_code_form({"code": code})
            if error:
                return ValidationResult.fail(error, code="validation_error")

            # Get session data
            session_data = session_store.get("verification", {})
            if not session_data:
                return ValidationResult.fail(
                    "Reset session expired",
                    code="session_expired"
                )

            session_code = session_data.get("code")
            session_expiry = session_data.get("expiry")

            # Validate code
            if not session_code or session_code != code.strip():
                return ValidationResult.fail(
                    "Invalid reset code",
                    code="invalid_code"
                )

            # Check expiry
            if session_expiry and time.time() > float(session_expiry):
                return ValidationResult.fail(
                    "Reset code has expired",
                    code="code_expired"
                )

            return ValidationResult.ok(
                message="Code verified",
                code="code_verified"
            )

        except Exception as e:
            errhandler(e, log="auth_service", path="services")
            return ValidationResult.fail(
                "An error occurred verifying code",
                code="verify_code_error"
            )

    def reset_password(
        self,
        new_password: str,
        confirm_password: str,
        session_store: dict
    ) -> ValidationResult:
        """
        Reset user password.
        """
        try:
            # Validate password format
            error = AuthValidator.validate_reset_password_form({
                "key": new_password,
                "key_check": confirm_password
            })
            if error:
                return ValidationResult.fail(error, code="validation_error")

            # Resolve user from session
            user = self.resolve_user_from_session(session_store)
            if not user:
                return ValidationResult.fail(
                    "User not found",
                    code="user_not_found"
                )

            # Check if new password is same as old
            if user.check_password(new_password):
                return ValidationResult.fail(
                    "New password must be different from old password",
                    code="same_password"
                )

            # Update password
            user.set_password(new_password)
            db.session.commit()

            # Clear session
            session_store.pop("verification", None)

            return ValidationResult.ok(
                message="Password reset successfully",
                code="password_reset_success",
                obj=user
            )

        except Exception as e:
            db.session.rollback()
            errhandler(e, log="auth_service", path="services")
            return ValidationResult.fail(
                "An error occurred resetting your password",
                code="password_reset_error"
            )