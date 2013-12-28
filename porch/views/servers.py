# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.views.servers
    ~~~~~~~~~~~~~~~~~~~

    Build servers configuration
'''

# Import POrch libs
from porch.application import *
from porch.forms import *

# Import 3rd-party libs
from jenkinsapi.jenkins import Jenkins
from jenkinsapi.custom_exceptions import JenkinsAPIException


# ----- Blueprints & Menu Entries --------------------------------------------------------------->
servers = Blueprint('servers', __name__, url_prefix='/build-servers')

main_category_link = main_nav.add_menu_entry(
    _('Build Servers'), 'servers.index', classes='fa fa-cogs',
    visiblewhen=check_wether_is_admin
)

servers_nav = build_context_nav('servers_view_nav')
servers_nav.add_menu_item(main_category_link)
servers_nav.add_menu_entry(
    _('New Server'), 'servers.new', priority=100, classes='fa fa-plus', li_classes='pull-right',
    visiblewhen=check_wether_is_admin
)
# <---- Blueprints & Menu Entries ----------------------------------------------------------------


# ----- Forms ----------------------------------------------------------------------------------->
class NewServerForm(DBBoundForm):

    title           = _('New Build Server')

    address         = URLField(_('Address'), validators=[url()])
    username        = TextField(_('Username'), validators=[DataRequired()])
    access_token    = PasswordField(_('Password'), validators=[DataRequired()])
    sync_builders   = BooleanField(_('Sync Server Builders'), default=True, description=_(
                        'Sync all available builders from the server upon creation'))

    # Actions
    add             = PrimarySubmitField(_('Add'))

    def validate_address(self, field):
        if BuildServer.query.get(field.data):
            raise ValidationError(
                _('There\'s already a build server matching the {0!r} address'.format(field.value))
            )

    def validate(self, extra_validators=None):
        rv = super(Form, self).validate()
        if not rv:
            return rv
        # No errors? Validate the connection to the Jenkins server
        try:
            jenkins = Jenkins(self.address.data,
                              username=self.username.data,
                              password=self.access_token.data)
            jenkins.poll()
        except JenkinsAPIException as exc:
            flash(Markup(
                _('Unable to authenticate user {0!r} against the {1!r} server.'.format(
                    self.username.data, self.address.data
                ))), 'danger'
            )
            return False
        return rv


class DeleteBuildServer(DBBoundForm):

    title           = _('Delete Build Server')

    id              = HiddenField('Server ID', validators=[DataRequired()])
    address         = URLField(_('Address'), validators=[DataRequired()])
    username        = TextField(_('Username'), validators=[DataRequired()])

    # Actions
    delete          = SensibleSubmitField(_('Delete'))


class EditBuildServer(DBBoundForm):

    title           = _('Edit Build Server')

    id              = HiddenField('Server ID', validators=[DataRequired()])
    address         = URLField(_('Address'), validators=[DataRequired()])
    username        = TextField(_('Username'), validators=[DataRequired()])
    access_token    = PasswordField(_('Password'), validators=[DataRequired()])

    # Actions
    update          = SubmitField(_('Update'))

    def validate(self, extra_validators=None):
        rv = super(Form, self).validate()
        if not rv:
            return rv
        # No errors? Validate the connection to the Jenkins server
        try:
            jenkins = Jenkins(self.address.data,
                              username=self.username.data,
                              password=self.access_token.data)
            jenkins.poll()
        except JenkinsAPIException as exc:
            flash(Markup(
                _('Unable to authenticate user {0!r} against the {1!r} server.'.format(
                    self.username.data, self.address.data
                ))), 'danger'
            )
            return False
        return rv
# <---- Forms ------------------------------------------------------------------------------------


# ----- Views ----------------------------------------------------------------------------------->
@servers.route('/')
@admin_permission.require(403)
def index():
    return render_template('servers/index.html', servers=BuildServer.query.all())


@servers.route('/new', methods=('GET', 'POST'))
@admin_permission.require(403)
def new():
    form = NewServerForm(formdata=request.values.copy())
    print 333, form.sync_builders.data
    if form.validate_on_submit():
        server = BuildServer(
            form.address.data,
            form.username.data,
            form.access_token.data
        )
        db.session.add(server)
        if form.sync_builders.data is True:
            for name, builder in server.jenkins_instance.iteritems():
                if not builder.is_active():
                    continue
                server.builders.add(
                    Builder(name, builder._data['displayName'], builder.get_description())
                )
        db.session.commit()
        return redirect_to('servers.index')
    return render_template('servers/new.html', form=form)


@servers.route('/edit/<int:server_id>', methods=('GET', 'POST'))
@admin_permission.require(403)
def edit(server_id):
    server = BuildServer.query.get(server_id)
    if not server:
        flash(_('No build server by the ID of {0!r} was found'.format(server_id)), 'danger')
        return redirect_back('servers.index')
    form = EditBuildServer(server, formdata=request.values.copy())
    if form.validate_on_submit():
        db.session.add(server)
        db.session.commit()
        flash(_('Build server updated'), 'info')
        return redirect_to('servers.index')
    return render_template('servers/edit.html', form=form)


@servers.route('/delete/<int:server_id>', methods=('GET', 'POST'))
@admin_permission.require(403)
def delete(server_id):
    server = BuildServer.query.get(server_id)
    if not server:
        flash(_('No build server by the ID of {0!r} was found'.format(server_id)), 'danger')
        return redirect_back('servers.index')
    form = DeleteBuildServer(server, formdata=request.values.copy())
    if form.validate_on_submit():
        db.session.delete(server)
        db.session.commit()
        flash(_('Build server deleted'), 'info')
        return redirect_to('servers.index')

    return render_template('servers/delete.html', form=form)


@servers.route('/sync/<int:server_id>', methods=('GET', 'POST'))
@admin_permission.require(403)
def sync(server_id):
    server = BuildServer.query.get(server_id)
    if not server:
        flash(_('No build server by the ID of {0!r} was found'.format(server_id)), 'danger')
        return redirect_back('servers.index')

    existing = server.builders
    existing_names = set([e.name for e in existing])
    new = removed = updated = 0
    unchanged = len(existing_names)
    for name, builder in server.jenkins_instance.iteritems():
        if name in existing_names:
            existing_names.remove(name)
            instance = Builder.query.get(name)
            description = builder.get_description()
            display_name = builder._data['displayName']
            if instance.description == description and instance.display_name == display_name:
                continue
            instance.description = description
            instance.display_name = display_name
            updated += 1
            continue

        if not builder.is_active():
            continue

        server.builders.add(
            Builder(name, builder._data['displayName'], builder.get_description())
        )
        new += 1
    for name in existing_names:
        builder = Builder.query.get(name)
        builder.removed = True
        removed += 1
    db.session.commit()
    flash(_('Synchronised server builders. New: {0}; Updated: {1}; Removed: {2}; '
            'Unchanged: {3};'.format(new, updated, removed,
                                     (unchanged - new - updated - removed))))
    return redirect_to('servers.index')
# <---- Views ------------------------------------------------------------------------------------
