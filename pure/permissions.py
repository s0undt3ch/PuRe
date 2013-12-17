# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    pure.permissions
    ~~~~~~~~~~~~~~~~

    Web-application permissions
'''
# pylint: disable=C0103

import logging
# pylint: disable=E0611,F0401
from flask.ext.principal import (AnonymousIdentity, Identity, Permission, Principal, RoleNeed,
                                 TypeNeed, identity_changed)
# pylint: enable=E0611,F0401
from saltprd.signals import application_configured

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
    # Finalize principal configuration
    principal.init_app(app)
# <---- Instantiate Principal --------------------------------------------------------------------
