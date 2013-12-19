# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.views.index
    ~~~~~~~~~~~~~~~~~

    The main application view
'''

# Import POrch libs
from porch.application import *


main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')
    return 'Bah!'
