# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.views.users
    ~~~~~~~~~~~~~~~~~

    Minimal user management
'''

# Import POrch libs
from porch.forms import *
from porch.application import *


# ----- Blueprints & Menu Entries --------------------------------------------------------------->
users = Blueprint('users', __name__, url_prefix='/users')

main_category_link = main_nav.add_menu_entry(
    _('Users'), 'users.index', classes='sensible', priority=-50,
    visiblewhen=check_wether_is_admin
)

users_nav = build_context_nav('users_view_nav')
# <---- Blueprints & Menu Entries ----------------------------------------------------------------


# ----- Forms ----------------------------------------------------------------------------------->
# <---- Forms ------------------------------------------------------------------------------------


# ----- Views ----------------------------------------------------------------------------------->
@users.route('/')
@administrator_permission.require(403)
def index():
    return render_template('users/index.html', users=Account.query.all())


@users.route('/permissions/<user_id>')
@administrator_permission.require(403)
def perms():
    return render_template('users/index.html', users=Account.query.all())
# <---- Views ------------------------------------------------------------------------------------
