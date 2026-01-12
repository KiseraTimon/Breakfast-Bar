from . import routes
from flask import render_template, redirect, url_for, flash, request

from flask_login import current_user

from website.services import MenuService

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

    service = MenuService()

    # Get query parameters
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Get user ID if logged in
    user_id = user.id if user else None

    # Get menu data
    menu_data = service.get_menu_data(
        category_id=category_id if category_id else None,
        search=search if search else None,
        page=page if page else None,
        per_page=per_page if per_page else None,
        user_id=user_id
    )

    return render_template(
        "menu/menu.html",
        title="Menu",
        user=user,
        menu=menu_data
    )

# Food Details
@routes.route("/menu/<int:item_id>")
def food(item_id):
    """
    Individual food item detail page.
    Shows full details, ingredients, reviews, etc.
    """
    if current_user.is_authenticated:
        user = current_user
    else:
        user = None

    service = MenuService()

    user_id = user.id if user else None

    item_data = service.get_food_item_details(
        food_item_id=item_id,
        user_id=user_id
    )

    if not item_data:
        abort(404)

    return render_template(
        "menu/food-details.html",
        title="Food",
        user=user,
        food=item_data
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