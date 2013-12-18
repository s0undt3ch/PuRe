# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    pure.database
    ~~~~~~~~~~~~~

    Database Support
'''
# pylint: disable=E8221

# Import Python libs
from datetime import datetime

# Import 3rd-party plugins
from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy

# Import PuRe libs
from pure.signals import application_configured


# ----- Simplify * Imports ---------------------------------------------------------------------->
ALL_DB_IMPORTS = [
    'db',
    'Account'
]
__all__ = ALL_DB_IMPORTS + ['ALL_DB_IMPORTS']
# <---- Simplify * Imports -----------------------------------------------------------------------


# ----- Instantiate the Plugin ------------------------------------------------------------------>
db = SQLAlchemy()


@application_configured.connect
def configure_sqlalchemy(app):
    db.init_app(app)
# <---- Instantiate the Plugin -------------------------------------------------------------------


# ----- Define the Models ----------------------------------------------------------------------->
class AccountQuery(db.Query):

    def get(self, id_or_login):
        if isinstance(id_or_login, basestring):
            return self.filter(Account.login == id_or_login).first()
        return db.Query.get(self, id_or_login)

    def from_github_token(self, token):
        return self.filter(Account.token == token).first()


class Account(db.Model):
    __tablename__   = 'accounts'

    id              = db.Column('github_id', db.Integer, primary_key=True)
    login           = db.Column('github_login', db.String(100))
    name            = db.Column('github_name', db.String(100))
    email           = db.Column('github_email', db.String(254))
    token           = db.Column('github_access_token', db.String(100), index=True, unique=True)
    avatar_url      = db.Column(db.String(2000))
    last_login      = db.Column(db.DateTime, default=datetime.utcnow)
    register_date   = orm.deferred(db.Column(db.DateTime))
    locale          = db.Column(db.String(10), default=lambda: 'en')
    timezone        = db.Column(db.String(25), default=lambda: 'UTC')

    # Consider https://github.com/dfm/osrc/blob/master/osrc/timezone.py

    query_class     = AccountQuery

    def __init__(self, id_, login, name, email, token, avatar_url):
        self.id = id_
        self.login = login
        self.name = name
        self.email = email
        self.token = token
        self.avatar_url = avatar_url

    def update_last_login(self):
        self.last_login = datetime.utcnow()
# <---- Define the Models ------------------------------------------------------------------------
