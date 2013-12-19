# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.scripts
    ~~~~~~~~~~~~~

    CLI scripts access
'''

# Import Porch libs
from porch.application import manager


def main():
    manager.run()


if __name__ == '__main__':
    main()
