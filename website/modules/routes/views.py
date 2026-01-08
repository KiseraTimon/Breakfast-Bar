from . import routes
from flask import render_template

from flask_login import current_user

# Homepage Route
@routes.route("/")
def homepage():
    if current_user.is_authenticated:
        user = current_user
    else:
        user = None
    return render_template(
        "home/index.html",
        user=user
    )

# Menu Route
@routes.route("/menu")
def menu():
    if current_user.is_authenticated:
        user = current_user
    else:
        user = None
    return render_template(
        "menu/menu.html",
        title="Menu",
        user=user
    )

# Food Details
@routes.route("/item")
def food():
    if current_user.is_authenticated:
        user = current_user
    else:
        user = None
    return render_template(
        "menu/food-details.html",
        title="Food",
        user=user
    )

# Services Route
@routes.route("/services")
def services():
    if current_user.is_authenticated:
        user = current_user
    else:
        user = None
    return render_template(
        "services/services.html",
        title="Services",
        user=user
    )

# Checkout Route
@routes.route("/checkout")
def checkout():
    if current_user.is_authenticated:
        user = current_user
    else:
        user = None
    return render_template(
        "checkout/checkout.html",
        title="Checkout",
        user=user
    )