# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import sys

from flask import Flask, render_template

from flaskshop.extensions import (
    babel,
    bcrypt,
    bootstrap,
    csrf_protect,
    db,
    debug_toolbar,
    login_manager,
    migrate,
    get_locale
)
from flaskshop.plugin import manager, spec
from flaskshop.plugin.models import PluginRegistry
from flaskshop.settings import Config
from flaskshop.utils import jinja_global_varibles
from flask_cors import CORS


def create_app(config_object=Config):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    app.pluggy = manager.FlaskshopPluginManager("flaskshop")
    register_extensions(app)
    load_plugins(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    jinja_global_varibles(app)
    
    
    
    return app


def include_cors(app):
    CORS(
        app,
        origins=["http://127.0.0.1:5000", "http://127.0.0.1:8000"],
        supports_credentials=True,          
        allow_headers=["Content-Type"],     
        methods=["POST"]                    
    )


def register_extensions(app):
    bcrypt.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)


def register_blueprints(app):
    app.pluggy.hook.flaskshop_load_blueprints(app=app)


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"errors/{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db}

    app.shell_context_processor(shell_context)




def load_plugins(app):
    app.pluggy.add_hookspecs(spec)

    for name, module in sys.modules.items():
        if name.startswith("flaskshop"):
            app.pluggy.register(module)

    app.pluggy.load_setuptools_entrypoints("flaskshop_plugins")
    try:
        with app.app_context():
            for name in app.pluggy.external_plugins:
                plugin, _ = PluginRegistry.get_or_create(name=name)
                if not plugin.enabled:
                    app.pluggy.set_blocked(plugin.name)
    except Exception as e:
        # when db migrate raise exception
        app.logger.error(e)
