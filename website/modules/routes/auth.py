from . import routes
from flask import render_template, redirect, url_for, request, session, flash

from flask_login import login_required, current_user, login_user, logout_user

from utils import errhandler

from website.models import User

from website.services import AuthService
from website.helpers import manager, mailer

from database import db

import time, random, secrets, string

# Logout Route
@routes.route("/logout")
@login_required
def logout():
    # Logout Data
    logout_data = session.get('logout', {})
    message = logout_data.get('message', "You have been logged out")
    category = logout_data.get('category', "warning")

    flash(message, category=category)

    # Clearing Sessions
    session.clear()

    # Logging Out User
    logout_user()

    # Redirecting
    return redirect(url_for("routes.homepage"))

# Signin Route
@routes.route("/signin", methods=['GET', 'POST'])
def signin():
    if ((current_user) and (current_user.is_authenticated) and (current_user.is_verified)):
        return redirect(url_for('routes.portal'))

    if ((current_user) and (current_user.is_authenticated) and (not (current_user.is_verified))):
        return redirect(url_for("routes.verify"))

    # POST Requests
    if request.method == "POST":
        # Initializing auth service
        auth_service = AuthService()

        result = auth_service.signin(
            identifier=request.form.get("identifier", ""),
            password=request.form.get("key", "")
        )

        if not result.success:
            flash(result.message, category="error")

            return redirect(request.url)

        user = result.object

        if user.is_verified:
            login_user(user)

            flash("You have been logged in successfully", category="success")
            return redirect(url_for('routes.portal'))
        else:
            # Send verification code
            session_man = manager(s=session_store, e=user.email)
            send_mail = mailer(s=session_store, r=user.email, m=0)

            if not (session_man and send_mail):
                session['logout'] = {
                    "message": "An error occured mailing your verification code. Contact Support",
                    "category": "error"
                }

                return redirect(url_for("routes.logout"))

            flash("Complete verification to continue", category="warning")
            return redirect(url_for("routes.verify"))

    return render_template("auth/auth.html")

# Signup Route
@routes.route("/signup", methods=['GET', 'POST'])
def signup():
    # Redirect if already authenticated
    if current_user and current_user.is_authenticated:
        if current_user.is_verified:
            return redirect(url_for("routes.portal"))
        return redirect(url_for("routes.verify"))

    # POST Requests
    if request.method == "POST":
        # Initializing auth service
        auth_service = AuthService()

        # Sign up
        result = auth_service.signup(request.form.to_dict())

        if not result.success:
            flash(result.message, category="error")
            return redirect(request.url)

        payload = result.object

        # Helpers sending verification mail
        session_man = manager(s=session, e=user.email)
        send_mail = mailer(s=session, r=user.email, m=0)

        if not (session_man and send_mail):
            # Error Message
            flash("An error occurred mailing your verification code. Contact support", category="error")

            return redirect(request.url)

        flash("Your account has been created successfully", category="success")
        return redirect(url_for("routes.verify"))

    return render_template("auth/auth.html")

# Password Reset Route
@routes.route("/reset-password")
def reset():
    return render_template("auth/auth.html")

# Verification Route
@routes.route("/verify", methods=['GET', 'POST'])
def verify():
    # Checking for authenticated & verified users
    if current_user.is_authenticated and current_user.is_verified:
        return redirect(url_for('routes.portal'))

    # POST Requests
    if request.method == "POST":
        # Initializing auth service
        auth_service = AuthService()

        # Handling Code Resend Requests
        mode = request.form.get("mode", "verify")

        if mode == "resend":
            # Resend code
            result = auth_service.resend_verification_code(
                current_user=current_user if current_user.is_authenticated else None,
                session_store=session
            )

            flash(result.message, category="success" if result.success else "error")
            return redirect(request.url)

        elif mode == "verify":
            # Verify code
            result = auth_service.verify_code(
                code=request.form.get("code", ""),
                current_user=current_user if current_user.is_authenticated else None,
                session_store=session
            )

            if not result.success:
                flash(result.message, category="error")
                return redirect(request.url)

            # Login user
            user = result.object
            login_user(user)

            flash("Account verified successfully", category="success")
            return redirect(url_for('routes.portal'))

        else:
            flash("Invalid access to service. Contact support", category="error")
            return redirect(request.url)

    return render_template("auth/auth.html")

# Password Reset Route
@routes.route("/reset-password", methods=['GET', 'POST'])
def reset():
    if request.method == "POST":
        # Initialize service
        auth_service = AuthService()

        mode = request.form.get("mode", "request")

        if mode == "request":
            # Request reset code
            result = auth_service.request_password_reset(
                email=request.form.get("email", ""),
                session_store=session
            )

            flash(result.message, category="success" if result.success else "error")
            return redirect(request.url)

        elif mode == "verify_code":
            # Verify reset code
            result = auth_service.verify_reset_code(
                code=request.form.get("code", ""),
                session_store=session
            )

            if not result.success:
                flash(result.message, category="error")
                return redirect(request.url)

            flash("Code verified. Enter your new password", category="success")
            return redirect(request.url)

        elif mode == "reset":
            # Reset password
            result = auth_service.reset_password(
                new_password=request.form.get("key", ""),
                confirm_password=request.form.get("key_check", ""),
                session_store=session
            )

            if not result.success:
                flash(result.message, category="error")
                return redirect(request.url)

            flash("Password reset successfully. Please sign in", category="success")
            return redirect(url_for("routes.signin"))

        else:
            flash("Invalid request", category="error")
            return redirect(request.url)

    return render_template("auth/auth.html")