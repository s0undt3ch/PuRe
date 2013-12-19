# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.permissions
    ~~~~~~~~~~~~~~~~~

    Web-application permissions
'''
# pylint: disable=C0103

# Import Python Libs
import logging

# Import 3rd-party Libs
import github
# pylint: disable=E0611,F0401
from flask.ext.principal import (AnonymousIdentity, Identity, Permission, Principal, RoleNeed,
                                 TypeNeed, identity_changed, identity_loaded, ActionNeed)
# pylint: enable=E0611,F0401
from sqlalchemy.exc import OperationalError
from porch.signals import after_identity_account_loaded, application_configured

log = logging.getLogger(__name__)

# ----- Simplify * Imports ---------------------------------------------------------------------->
ALL_PERMISSION_IMPORTS = [
    'admin_permission',
    'manager_permission',
    'admin_or_manager_permission',
    'anonymous_permission',
    'authenticated_permission',
    'identity_changed',
    'Identity',
    'AnonymousIdentity',
]
__all__ = ALL_PERMISSION_IMPORTS + ['ALL_PERMISSION_IMPORTS']
# <---- Simplify * Imports -----------------------------------------------------------------------


# ----- Default Roles & Permissions ------------------------------------------------------------->
admin_role = RoleNeed('administrator')
admin_permission = Permission(admin_role)

manager_role = RoleNeed('manager')
manager_permission = Permission(manager_role)

admin_or_manager_permission = Permission(admin_role, manager_role)

anonymous_permission = Permission()
authenticated_permission = Permission(TypeNeed('authenticated'))
# <---- Default Roles & Permissions --------------------------------------------------------------


# ----- Instantiate Principal ------------------------------------------------------------------->
principal = Principal(use_sessions=True, skip_static=True)


@application_configured.connect
def on_application_configured(app):
    from porch.database import db, Account

    # Finalize principal configuration
    principal.init_app(app)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        log.debug('Identity loaded: {0}'.format(identity))

        if not identity.auth_type:
            identity.account = None
            return

        try:
            identity.account = account = Account.query.get(int(identity.id))
            if account is not None:
                log.debug('User {0!r} loaded from identity {1}'.format(account.login, identity))
                account.update_last_login()
                identity.provides.add(TypeNeed('authenticated'))
                # Update the privileges that a user has
                for privilege in account.privileges:
                    identity.provides.add(ActionNeed(privilege.name))
                for group in account.groups:
                    # And for each of the groups the user belongs to
                    for privilege in group.privileges:
                        # Add the group privileges to the user
                        identity.provides.add(RoleNeed(privilege.name))
                # Setup this user's github api access
                identity.github = github.Github(
                    account.token,
                    client_id=app.config.get('GITHUB_CLIENT_ID'),
                    client_secret=app.config.get('GITHUB_CLIENT_SECRET')
                )
                after_identity_account_loaded.send(sender, account=identity.account)
        except OperationalError:
            # Database has not yet been setup
            pass


@principal.identity_saver
def save_request_identity(identity):
    # Late import
    from porch.database import db, Account
    log.debug('On save_request_identity: {0}'.format(identity))
    if getattr(identity, 'account', None) is None:
        log.debug('No account associated with identity. Nothing to store.')
        return

    for need in identity.provides:
        log.debug('Identity {0!r} provides: {1}'.format(identity, need))
        if need.method in ('type', 'role'):
            # We won't store type methods, ie, "authenticated", nor, role
            # methods which are permissions belonging to groups and managed
            # on a future administration panel.
            continue

        #privilege = models.Privilege.query.get(need)
        #if not privilege:
        #    log.debug('Privilege {0!r} does not exist. Creating...'.format(need))
        #    privilege = models.Privilege(need)
        #
        #if privilege not in identity.account.privileges:
        #    identity.account.privileges.add(privilege)
    db.session.commit()
# <---- Instantiate Principal --------------------------------------------------------------------
