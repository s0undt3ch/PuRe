# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    pure.views.account
    ~~~~~~~~~~~~~~~~~~

    Account related views
'''

from pure.application import *

# ----- Blueprints & Menu Entries --------------------------------------------------------------->
account = Blueprint('account', __name__, url_prefix='/account')
# <---- Blueprints & Menu Entries ----------------------------------------------------------------


# ----- Forms ----------------------------------------------------------------------------------->

# <---- Forms ------------------------------------------------------------------------------------


# ----- Views ----------------------------------------------------------------------------------->
@account.route('/signin', methods=('GET',))
def signin():
    pass
# <---- Views ------------------------------------------------------------------------------------
