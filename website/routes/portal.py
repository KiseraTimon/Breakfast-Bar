from . import routes
from flask import render_template, redirect, url_for, request, session

from flask_login import login_required, current_user

from website.models import UserRole
from website.services import DashboardService

from functools import wraps

# Decorator for Dashboard Access Roles
def roles_required(*allowed_roles):
    """
    Restricts access to users with one of the specified roles.
    Usage:
        @roles_required(UserRole.ADMIN)
        @roles_required(UserRole.STAFF, UserRole.ADMIN)
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if (
                not current_user.is_authenticated or
                current_user.role not in allowed_roles
            ):
                session['logout'] = {
                    "message": "You are not authorized to access this page. Re-authenticate to continue",
                    "category": "error"
                }
                return redirect(url_for('routes.logout'))
            return f(*args, **kwargs)
        return wrapped
    return decorator


@routes.route("/portal")
@login_required
def portal():
    """
    Central dispatcher that routes authenticated users
    to their correct dashboard based on role.
    """
    role = current_user.role

    if role == UserRole.ADMIN:
        return redirect(url_for('routes.admin'))

    if role == UserRole.STAFF:
        return redirect(url_for('routes.staff'))

    if role == UserRole.CUSTOMER:
        return redirect(url_for('routes.customer'))

    # Fallback safety
    session['logout'] = {
        "message": "Invalid account role. Contact support.",
        "category": "error"
    }
    return redirect(url_for('routes.logout'))


# Customer Dashboard Route
@routes.route("/dashboard", methods=['GET', 'POST'])
@login_required
@roles_required(UserRole.CUSTOMER)
def customer():

    # Dashboard Service Object
    dashboard = DashboardService()

    # POST Requests
    if request.method == "POST":
        pass

    # Retrieving Details
    data = dashboard.get_dashboard_data(
        user_id=current_user.id
    )

    return render_template(
        "dashboard/customer.html",
        title="Dashboard",
        user=current_user,
        data=data
    )

# Staff Dashboard
@routes.route("/staff")
@login_required
@roles_required(UserRole.STAFF, UserRole.ADMIN)
def staff():

    return render_template(
        "dashboard/customer.html",
        title="Dashboard",
        user=current_user
    )

# Admin Dashboard Route
@routes.route("/administrator")
@login_required
@roles_required(UserRole.ADMIN)
def admin():

    return render_template(
        "dashboard/admin.html",
        title="Dashboard",
        user=current_user
    )