from flask import flash, redirect, render_template, request, url_for

from flaskshop.account.utils import admin_required
from flaskshop.checkout.models import ShippingMethod
from flaskshop.dashboard.forms import (
    DashboardMenuForm,
    ShippingMethodForm,
    SiteMenuForm,
    SitePageForm,
    generate_settings_form,
)
from flaskshop.dashboard.utils import wrap_partial, item_del
from flaskshop.dashboard.models import DashboardMenu, Setting
from flaskshop.plugin.models import PluginRegistry
from flaskshop.product.models import Category, Collection
from flaskshop.public.models import MenuItem, Page


def shipping_methods():
    page = request.args.get("page", type=int, default=1)
    pagination = ShippingMethod.query.paginate(page=page, per_page=10)
    props = {
        "id": ("ID"),
        "title": ("Title"),
        "price_human": ("Price"),
        "created_at": ("Created At"),
    }
    context = {
        "title": ("Shipping Method"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "shipping_methods",
    }
    return render_template("dashboard/general_list.html", **context)


def shipping_methods_manage(id=None):
    if id:
        shipping_method = ShippingMethod.get_by_id(id)
        form = ShippingMethodForm(obj=shipping_method)
    else:
        shipping_method = ShippingMethod()
        form = ShippingMethodForm()
    if form.validate_on_submit():
        form.populate_obj(shipping_method)
        shipping_method.save()
        flash(("Shipping method saved."), "success")
        return redirect(url_for("dashboard.shipping_methods"))
    return render_template(
        "general_edit.html", form=form, title=("Shipping Method")
    )


shipping_methods_del = wrap_partial(item_del, ShippingMethod)


def site_menus():
    page = request.args.get("page", type=int, default=1)
    pagination = MenuItem.query.paginate(page=page, per_page=10)
    props = {
        "id": ("ID"),
        "title": ("Title"),
        "order": ("Order"),
        "position": ("Position"),
        "parent_id": ("Parent Id"),
    }
    context = {
        "title": ("Site Menus"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "site_menus",
    }
    return render_template("dashboard/general_list.html", **context)


@admin_required
def site_menus_manage(id=None):
    if id:
        menu = MenuItem.get_by_id(id)
        form = SiteMenuForm(obj=menu)
    else:
        menu = MenuItem()
        form = SiteMenuForm()
    form.parent_id.choices = [(m.id, m.title) for m in MenuItem.first_level_items()]
    form.parent_id.choices.insert(0, (0, "None"))
    form.category_id.choices = [(c.id, c.title) for c in Category.query.all()]
    form.category_id.choices.insert(0, (0, "None"))
    form.collection_id.choices = [(c.id, c.title) for c in Collection.query.all()]
    form.collection_id.choices.insert(0, (0, "None"))
    form.page_id.choices = [(p.id, p.title) for p in Page.query.all()]
    form.page_id.choices.insert(0, (0, "None"))

    if form.validate_on_submit():
        form.populate_obj(menu)
        menu.save()
        flash(("Menu saved."), "success")
        return redirect(url_for("dashboard.site_menus"))

    return render_template(
        "general_edit.html", form=form, title=("Site Menu")
    )


site_menu_del = wrap_partial(item_del, MenuItem)


def dashboard_menus():
    page = request.args.get("page", type=int, default=1)
    pagination = DashboardMenu.query.paginate(page=page, per_page=10)
    props = {
        "id": ("ID"),
        "title": ("Title"),
        "order": ("Order"),
        "endpoint": ("Endpoint"),
        "icon_cls": ("Icon class"),
        "parent_id": ("Parent Id"),
    }
    context = {
        "title": ("Dashboard Menus"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "dashboard_menus",
    }
    return render_template("dashboard/general_list.html", **context)


@admin_required
def dashboard_menus_manage(id=None):
    if id:
        menu = DashboardMenu.get_by_id(id)
        form = DashboardMenuForm(obj=menu)
    else:
        menu = DashboardMenu()
        form = DashboardMenuForm()
    form.parent_id.choices = [
        (d.id, d.title) for d in DashboardMenu.first_level_items()
    ]
    form.parent_id.choices.insert(0, (0, "None"))
    if form.validate_on_submit():
        form.populate_obj(menu)
        menu.save()
        flash(("Menu saved."), "success")
        return redirect(url_for("dashboard.dashboard_menus"))
    return render_template(
        "general_edit.html", form=form, title=("Dashboard Menu")
    )


dashboard_menu_del = wrap_partial(item_del, DashboardMenu)


def site_pages():
    page = request.args.get("page", type=int, default=1)
    pagination = Page.query.paginate(page=page, per_page=10)
    props = {
        "id": ("ID"),
        "title": ("Title"),
        "slug": ("Slug"),
        "url": ("Url"),
        "is_visible": ("Is Visiable"),
    }
    context = {
        "title": ("Site Pages"),
        "items": pagination.items,
        "props": props,
        "pagination": pagination,
        "identity": "site_pages",
    }
    return render_template("dashboard/general_list.html", **context)


def site_pages_manage(id=None):
    if id:
        page = Page.get_by_id(id)
        form = SitePageForm(obj=page)
    else:
        page = Page()
        form = SitePageForm()
    if form.validate_on_submit():
        form.populate_obj(page)
        page.save()
        flash(("Page saved."), "success")
        return redirect(url_for("dashboard.site_pages"))
    return render_template("site/site_page.html", form=form)


site_page_del = wrap_partial(item_del, Page)


def plugin_list():
    plugins = PluginRegistry.query.all()
    return render_template("site/plugin.html", plugins=plugins)


def plugin_enable(id):
    plugin = PluginRegistry.get_by_id(id)
    plugin.enabled = True
    plugin.save()
    flash(
        ("The plugin is enabled, Please restart flask-shop now!"), "success"
    )
    return redirect(url_for("dashboard.plugin_list"))


def plugin_disable(id):
    plugin = PluginRegistry.get_by_id(id)
    plugin.enabled = False
    plugin.save()
    flash(
        ("The plugin is disabled, Please restart flask-shop now!"), "info"
    )
    return redirect(url_for("dashboard.plugin_list"))


def site_setting():
    settings = Setting.query.all()
    form = generate_settings_form(settings)()

    old_settings = Setting.get_settings()
    if request.method == "GET":
        for key, value in old_settings.items():
            try:
                form[key].data = value
            except (KeyError, ValueError):
                pass

    if form.validate_on_submit():
        new_settings = {}
        for key, value in old_settings.items():
            try:
                # check if the value has changed
                if value == form[key].data:
                    continue
                else:
                    new_settings[key] = form[key].data
            except KeyError:
                pass
        Setting.update(settings=new_settings)
        flash(("Settings saved."), "success")
    return render_template(
        "general_edit.html", form=form, title=("Site Settings")
    )


def config_index():
    return render_template("site/index.html")
