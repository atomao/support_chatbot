# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, current_app, render_template, request, send_from_directory
from pluggy import HookimplMarker
from flask_login import current_user

from flaskshop.account.models import User
from flaskshop.extensions import login_manager
from flaskshop.product.models import Product

from .models import Page
from .search import Item

impl = HookimplMarker("flaskshop")


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.get_by_id(int(user_id))


def home():
    products = Product.get_featured_product()
    return render_template("public/home.html", products=products)


def style():
    return render_template("public/style_guide.html")


def favicon():
    return send_from_directory("static", "favicon-32x32.png")


def search():
    query = request.args.get("q", "")
    page = request.args.get("page", default=1, type=int)
    if current_app.config["USE_ES"]:
        pagination = Item.new_search(query, page)
    else:
        pagination = Product.query.filter(Product.title.ilike(f"%{query}%")).paginate(
            page=page, per_page=10
        )
    return render_template(
        "public/search_result.html",
        products=pagination.items,
        query=query,
        pagination=pagination,
    )


def show_page(identity):
    page = Page.get_by_identity(identity)
    return render_template("public/page.html", page=page)


def get_current_user(user_id):
    """Load user by ID."""
    user = User.get_by_id(user_id)
    return dict(
        username = user.username,
        user_id = str(user.id),
        email = user.email
    )



@impl
def flaskshop_load_blueprints(app):
    bp = Blueprint("public", __name__)
    bp.add_url_rule("/", view_func=home)
    bp.add_url_rule("/style", view_func=style)
    bp.add_url_rule("/favicon.ico", view_func=favicon)
    bp.add_url_rule("/search", view_func=search)
    bp.add_url_rule("/page/<identity>", view_func=show_page)
    bp.add_url_rule("/get_current_user/<int:user_id>", view_func = get_current_user)
    app.register_blueprint(bp)
