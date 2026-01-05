from . import routes
from flask import render_template, redirect, url_for, request, session, flash

from flask_login import login_required, current_user, login_user, logout_user

from utils import errhandler

from website.models import User

from website.modules.routes.validators import *

from database import db

# Logout Route
@routes.route("/logout")
@login_required
def logout():
    pass

# Signin Route
@routes.route("/signin", methods=['GET', 'POST'])
def signin():
    if ((current_user) and (current_user.is_authenticated) and (current_user.is_active)):
        return redirect(url_for('routes.dashboard'))

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

            return redirect(url_for('routes.dashboard'))

    return render_template("auth/auth.html")

# Signup Route
@routes.route("/signup", methods=['GET', 'POST'])
def signup():
    if (current_user) and (current_user.is_active):
        return redirect(url_for("routes.dashboard"))

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

            login_user(user)

        except Exception as e:
            db.session.rollback()

            flash("An error occurred creating your account. Contact support", category="error")

            errhandler(e, log="signup", path="auth")

            return redirect(request.url)

        else:
            flash("Your account has been created successfully", category="success")

            db.session.close()

            return redirect(url_for("routes.homepage"))

    return render_template("auth/auth.html")

# Password Reset Route
@routes.route("/reset-password")
def reset():
    return render_template("auth/auth.html")

# Verification Route
@routes.route("/verify")
@login_required
def verify():
    return render_template("auth/auth.html")