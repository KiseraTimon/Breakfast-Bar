from . import routes
from flask import render_template, redirect, url_for, request, session, flash

from flask_login import login_required, current_user, login_user, logout_user

from utils import errhandler

from website.models import User

from website.modules.routes.validators import *
from website.helpers import generator, manager, mailer

from database import db

import time, random, secrets, string

# Logout Route
@routes.route("/logout")
@login_required
def logout():
    # Logout Data
    logout_data = session.get('logout', {})

    message = logout_data.get('message', None)
    category = logout_data.get('category', None)

    if (message and category):
        flash(message, category=category)

    else:
        flash("You have been logged out", category="success")

    # Clearing Sessions
    session.clear()

    # Logging Out User
    logout_user()

    # Redirecting
    return redirect(url_for("routes.homepage"))

# Signin Route
@routes.route("/signin", methods=['GET', 'POST'])
def signin():
    if ((current_user) and (current_user.is_authenticated) and (current_user.is_active)):
        return redirect(url_for('routes.portal'))

    if ((current_user) and (current_user.is_authenticated) and (not (current_user.is_active))):
        return redirect(url_for("routes.verify"))

    # POST Requests
    if request.method == "POST":
        # Validator Object
        validator = SigninValidator(
            form=request.form.to_dict(),
            method=request.method
        )

        # Validating User
        result = validator.validate()

        if not result.success:
            flash(result.errors[0] if result.errors else "An error occurred creating your account. Contact  support", category="error")

            return redirect(request.url)

        user = result.object

        try:
            login_user(user)

        except Exception as e:
            errhandler(e, log="signin", path="auth")

            flash("An error occurred signing you in. Contact support", category="error")

            return redirect(url_for("routes.homepage"))
        else:
            flash("You have been logged in successfully", category="success")

            if ((user) and (user.is_authenticated) and (not (user.is_active))):
                return redirect(url_for("routes.verify"))

            return redirect(url_for('routes.portal'))

    return render_template("auth/auth.html")

# Signup Route
@routes.route("/signup", methods=['GET', 'POST'])
def signup():
    if (current_user) and (current_user.is_active):
        return redirect(url_for("routes.portal"))

    if ((current_user) and (current_user.is_authenticated) and (not (current_user.is_active))):
        return redirect(url_for("routes.verify"))

    # POST Requests
    if request.method == "POST":
        # Validator Object
        validator = SignupValidator(
            form = request.form.to_dict(),
            method = request.method
        )

        # Validating User
        result = validator.validate()

        if not result.success:
            flash(result.errors[0] if result.errors else "An error occurred creating your account. Contact  support", category="error")

            return redirect(request.url)

        payload = result.object

        try:
            user = User(
                first_name = payload['first_name'],
                last_name = payload['last_name'],
                email = payload['email'],
                phone = payload['phone']
            )

            user.set_password(password=payload['password'])
            user.update_status(active=False)
            user.update_last_login()

            db.session.add(user)
            db.session.commit()

            # Helpers
            manager(user.email)
            mailer(mode = 0)

        except Exception as e:
            db.session.rollback()

            flash("An error occurred creating your account. Contact support", category="error")

            errhandler(e, log="signup", path="auth")

            return redirect(request.url)

        else:
            flash("Your account has been created successfully", category="success")

            db.session.close()

            return redirect(url_for("routes.verify"))

    return render_template("auth/auth.html")

# Password Reset Route
@routes.route("/reset-password")
def reset():
    return render_template("auth/auth.html")

# Verification Route
@routes.route("/verify")
def verify():

    if (current_user.is_authenticated) and (current_user.is_active):
        return redirect(url_for('routes.portal'))

    # POST Requests
    if request.method == "POST":
        # Validator Object
        validator = VerifyValidator(
            form=request.form.to_dict(),
            method=request.method
        )

        # Handling Code Resend Requests
        mode = request.form.get("mode", "verify")
        if mode == "resend":
            manager(session['verification']['email'])
            mailer(mode = 0)

            flash("A new verification code has been sent to your email", category="success")

            return redirect(url_for('routes.verify'))

        # Validating User
        result = validator.validate()

        if not result.success:
            flash(result.errors[0] if result.errors else "An error occurred verifying your account. Contact support", category="error")

            return redirect(request.url)

        user = result.object

        try:
            login_user(user)

        except Exception as e:
            errhandler(e, log="verify", path="auth")

            flash("An error occurred verifying your account. Contact support", category="error")

            return redirect(url_for("routes.homepage"))
        else:
            flash("You have been authenticated & verified successfully", category="success")

            return redirect(url_for('routes.portal'))

    return render_template("auth/auth.html")