# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    pure.application
    ~~~~~~~~~~~~~~~~
'''
# Let's make PyLint not complain about our module global lowercased variables
# pylint: disable=C0103

# Import python libs
import os
import sys

# Import Flask libs & plugins
from flask import Blueprint, Flask, g, render_template, flash
from flask_babel import Babel, gettext as _
from flask_script import Manager
from flask_menubuilder import MenuBuilder

# Import PuRe libs
from pure.signals import application_configured, configuration_loaded

# ----- Simplify * Imports ---------------------------------------------------------------------->
__all__ = [
    '_',
    'g',
    'app',
    'flash',
    'Blueprint',
    'render_template'
]
# <---- Simplify * Imports -----------------------------------------------------------------------

# ----- Setup The Flask Application ------------------------------------------------------------->
# First we instantiate the application object
app = Flask(__name__)


def configure_app(config):
    '''
    Configure App hook
    '''
    sys.path.insert(0, os.path.abspath(config))
    try:
        import appconfig  # pylint: disable=F0401
        app.config.from_object(appconfig)
    except ImportError:
        pass
    configuration_loaded.send(app)
    return app


# Scripts Support
manager = Manager(configure_app)
#manager.add_command('db', MigrateCommand)
manager.add_option('-c', '--config', dest='config', required=False)

# I18N & L10N Support
babel = Babel(app)

# Menus
menus = MenuBuilder(app)


@configuration_loaded.connect
def on_configuration_loaded(app):
    '''
    Once the configuration is loaded hook
    '''

    # If we're debugging...
    if app.debug:
        # LessCSS Support
        from flask_sass import Sass
        sass = Sass(app)

        from werkzeug.debug import DebuggedApplication
        app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

    application_configured.send(app)
# <---- Setup The Flask Application --------------------------------------------------------------

# ----- Setup The Web-Application Views --------------------------------------------------------->
from pure.views.main import main
from pure.views.account import account

app.register_blueprint(main)
app.register_blueprint(account)
# <---- Setup The Web-Application Views ----------------------------------------------------------
