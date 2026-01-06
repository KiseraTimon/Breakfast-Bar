from . import routes
from flask import render_template, redirect, url_for

from flask_login import login_required, current_user

from website.models import UserRole

"""Access rules for routes"""
def is_active_user():
    return current_user.is_authenticated and current_user.is_active

def is_customer():
    return is_active_user() and current_user.role == UserRole.CUSTOMER

def is_staff():
    return is_active_user() and current_user.role == UserRole.STAFF

def is_admin():
    return is_active_user() and current_user.role == UserRole.ADMIN

# Dashboard Route
@routes.route("/portal")
@login_required
def portal():

    if is_customer():
        return redirect(url_for('routes.customer'))

    if is_staff():
        return redirect(url_for('routes.staff'))

    if is_admin():
        return redirect(url_for('routes.admin'))

    session['logout'] = {
        "message": "You are not authorized to access this page. Re-authenticate to continue",
        "category": "error"
    }
    return redirect(url_for('routes.logout'))

# Customer Dashboard Route
@routes.route("/dashboard")
@login_required
def customer():
    if not is_customer():
        # Logout Data
        session['logout'] = {
            "message": "You are not authorized to access this page. Re-authenticate to continue",
            "category": "error"
        }

        return redirect(url_for('routes.logout'))
    return render_template("dashboard/dashboard.html")

# Staff Dashboard
@routes.route("/staff")
@login_required
def staff():
    if not is_staff():
        # Logout Data
        session['logout'] = {
            "message": "You are not authorized to access this page. Re-authenticate to continue",
            "category": "error"
        }

        return redirect(url_for('routes.logout'))
    return render_template("dashboard/dashboard.html")

# Admin Dashboard Route
@routes.route("/administrator")
def admin():
    if not is_admin():
        # Logout Data
        session['logout'] = {
            "message": "You are not authorized to access this page. Re-authenticate to continue",
            "category": "error"
        }

        return redirect(url_for('routes.logout'))
    return render_template("dashboard/admin.html")