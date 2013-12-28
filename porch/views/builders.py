# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.views.builders
    ~~~~~~~~~~~~~~~~~~~~

    Builders, ie, Jenkins build configurations
'''

# Import POrch libs
from porch.forms import *
from porch.application import *


# ----- Blueprints & Menu Entries --------------------------------------------------------------->
builders = Blueprint('builders', __name__, url_prefix='/builders')

main_category_link = main_nav.add_menu_entry(
    _('Builders'), 'builders.index', classes='fa fa-cogs',
    visiblewhen=check_wether_is_manager_or_admin
)

builders_nav = build_context_nav('builders_view_nav')
builders_nav.add_menu_item(main_category_link)
# <---- Blueprints & Menu Entries ----------------------------------------------------------------


# ----- Forms ----------------------------------------------------------------------------------->
class DeleteBuilderForm(DBBoundForm):

    title           = _('Delete Builder')

    name            = HiddenField('Builder Name', validators=[DataRequired()])
    display_name    = URLField(_('Display Name'))

    # Actions
    delete          = SensibleSubmitField(_('Delete'))
# <---- Forms ------------------------------------------------------------------------------------


# ----- Views ----------------------------------------------------------------------------------->
@builders.route('/')
@admin_or_manager_permission.require(403)
def index():
    return render_template('builders/index.html', builders=Builder.query.all())


@builders.route('/delete/<builder_name>', methods=('GET', 'POST'))
@admin_or_manager_permission.require(403)
def delete(builder_name):
    builder = Builder.query.get(builder_name)
    if not builder:
        flash(_('No builder by the name of {0!r} was found'.format(builder_name)), 'danger')
        return redirect_back('builders.index')

    form = DeleteBuilderForm(builder, formdata=request.values.copy())
    if form.validate_on_submit():
        db.session.delete(builder)
        db.session.commit()
        flash(_('Builder deleted'), 'info')
        return redirect_to('builders.index')

    return render_template('builders/delete.html', form=form)
# <---- Views ------------------------------------------------------------------------------------
