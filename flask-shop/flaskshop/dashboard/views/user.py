from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import or_

from flaskshop.account.models import Role, User, UserAddress, UserRole
from flaskshop.dashboard.forms import UserAddressForm, UserForm
from flaskshop.dashboard.utils import wrap_partial, item_del
from flaskshop.order.models import Order


def users():
    page = request.args.get("page", type=int, default=1)
    search_word = request.args.get("keyword")
    query = User.query
    if search_word:
        query = query.filter(
            or_(
                User.username.like("%" + search_word + "%"),
                User.email.like("%" + search_word + "%"),
            )
        )
    pagination = query.paginate(page=page, per_page=10)
    props = {
        "id": ("ID"),
        "username": ("Username"),
        "email": ("Email"),
        "is_active_human": ("Is Active"),
    }
    context = {
        "title": ("User List"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
    }
    return render_template("user/list.html", **context)


def user(user_id):
    user = User.get_by_id(user_id)
    addresses = user.addresses
    orders = Order.get_user_orders(user_id)
    context = {"user": user, "addresses": addresses, "orders": orders}
    return render_template("user/detail.html", **context)


def user_edit(user_id):
    user = User.get_by_id(user_id)
    form = UserForm(obj=user)
    if form.validate_on_submit():
        if not form.password.data:
            del form.password

        form.populate_obj(user)
        user.save()
        selected_role = form.role.data
        if selected_role != "0":
            selected_role = Role.query.filter(Role.name == selected_role).first()
            user_role = UserRole.query.filter(
                UserRole.user_id == current_user.id,
                UserRole.role_id >= selected_role.id,
            ).first()
            user_role = Role.query.filter(Role.id == user_role.role_id).first()
            if selected_role.permissions > user_role.permissions:
                flash("You have no access rights", "warning")
            else:
                UserRole.query.filter(UserRole.user_id == user.id).delete()
                UserRole.create(user_id=user.id, role_id=selected_role.id)
        flash(("User saved."), "success")
        return redirect(url_for("dashboard.user", user_id=user_id))
    return render_template("general_edit.html", form=form, title=("User"))


user_del = wrap_partial(item_del, User)


def address_edit(id):
    addr = UserAddress.get_by_id(id)
    form = UserAddressForm(obj=addr)
    if form.validate_on_submit():
        form.populate_obj(addr)
        addr.save()
        flash(("Address saved."), "success")
        return redirect(url_for("dashboard.user", user_id=addr.user_id))
    return render_template(
        "general_edit.html", form=form, title=("User Address")
    )
