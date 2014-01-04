# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.views.groups
    ~~~~~~~~~~~~~~~~~

    Minimal group management
'''

# Import POrch libs
from porch.forms import *
from porch.application import *


# ----- Blueprints & Menu Entries --------------------------------------------------------------->
groups = Blueprint('groups', __name__, url_prefix='/groups')

main_category_link = main_nav.add_menu_entry(
    _('Groups'), 'groups.index', classes='sensible', priority=-40,
    visiblewhen=check_wether_is_admin
)

groups_nav = build_context_nav('groups_view_nav')
groups_nav.add_menu_entry(
    glyphiconer('plus') + _('New Group'), 'groups.new', priority=100,
    visiblewhen=check_wether_is_admin
)
# <---- Blueprints & Menu Entries ----------------------------------------------------------------


# ----- Forms ----------------------------------------------------------------------------------->
# <---- Forms ------------------------------------------------------------------------------------


# ----- Views ----------------------------------------------------------------------------------->
@groups.route('/')
@administrator_permission.require(403)
def index():
    return render_template('groups/index.html', groups=Group.query.all())


@groups.route('/new')
@administrator_permission.require(403)
def new():
    pass


@groups.route('/edit/<group_id>', methods=('GET', 'POST'))
@administrator_permission.require(403)
def edit(group_id):
    pass


@groups.route('/edit/<group_id>', methods=('GET', 'POST'))
@administrator_permission.require(403)
def delete(group_id):
    pass
# <---- Views ------------------------------------------------------------------------------------
