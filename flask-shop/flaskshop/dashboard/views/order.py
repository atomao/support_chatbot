from flask import render_template, request, flash

from flaskshop.constant import OrderStatusKinds
from flaskshop.order.models import Order


def orders():
    page = request.args.get("page", type=int, default=1)
    query = Order.query.order_by(Order.id.desc())

    status = request.args.get("status", type=int)
    if status:
        query = query.filter_by(status=status)
    order_no = request.args.get("order_number", type=str)
    if order_no:
        query = query.filter(Order.token.like(f"%{order_no}%"))
    created_at = request.args.get("created_at", type=str)
    if created_at:
        query = query.filter(Order.created_at >= created_at)
    ended_at = request.args.get("ended_at", type=str)
    if ended_at:
        query = query.filter(Order.created_at <= ended_at)
    pagination = query.paginate(page=page, per_page=10)
    props = {
        "id": ("ID"),
        "identity": ("Identity"),
        "status_human": ("Status"),
        "total_human": ("Total"),
        "user": ("User"),
        "created_at": ("Created At"),
    }
    context = {
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "order_stats_kinds": OrderStatusKinds,
    }
    return render_template("order/list.html", **context)


def order_detail(id):
    order = Order.get_by_id(id)
    return render_template("order/detail.html", order=order)


def send_order(id):
    order = Order.get_by_id(id)
    order.delivered()
    flash(("Order is sent."), "success")
    return render_template("order/detail.html", order=order)


def draft_order(id):
    order = Order.get_by_id(id)
    order.draft()
    flash(("Order is draft."), "success")
    return render_template("order/detail.html", order=order)
