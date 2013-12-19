# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Pedro Algarvio (pedro@algarvio.me)`
    :copyright: © 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    porch.database
    ~~~~~~~~~~~~~~

    Database Support
'''
# pylint: disable=E8221,C0103

# Import Python libs
from datetime import datetime

# Import 3rd-party plugins
from sqlalchemy import orm
from flask_sqlalchemy import SQLAlchemy

# Import POrch libs
from porch.signals import application_configured


# ----- Simplify * Imports ---------------------------------------------------------------------->
ALL_DB_IMPORTS = [
    'db',
    'Account',
    'Group',
    'Privilege'
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

    # Relations
    groups          = None  # Defined on Group
    privileges      = db.relation('Privilege', secondary='account_privileges',
                                  backref='privileged_accounts', lazy=True, collection_class=set,
                                  cascade='all, delete')

    def __init__(self, id_, login, name, email, token, avatar_url):
        self.id = id_
        self.login = login
        self.name = name
        self.email = email
        self.token = token
        self.avatar_url = avatar_url

    def update_last_login(self):
        self.last_login = datetime.utcnow()


class GroupQuery(db.Query):

    def get(self, privilege):
        if isinstance(privilege, basestring):
            return self.filter(Group.name == privilege).first()
        return db.Query.get(self, privilege)


class Group(db.Model):
    __tablename__ = 'groups'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(30))

    accounts      = db.dynamic_loader('Account', secondary='group_accounts',
                                      backref=db.backref(
                                          'groups', lazy=True, collection_class=set
                                      ))
    privileges    = db.relation('Privilege', secondary='group_privileges',
                                backref='privileged_groups', lazy=True, collection_class=set,
                                cascade='all, delete')

    query_class   = GroupQuery

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return u'<{0} {1!r}:{2!r}>'.format(self.__class__.__name__, self.id, self.name)


group_accounts = db.Table(
    'group_accounts', db.metadata,
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('account_github_id', db.Integer, db.ForeignKey('accounts.github_id'))
)


group_privileges = db.Table(
    'group_privileges', db.metadata,
    db.Column('group_id', db.Integer, db.ForeignKey('groups.id')),
    db.Column('privilege_id', db.Integer, db.ForeignKey('privileges.id'))
)


class PrivilegeQuery(orm.Query):
    def get(self, privilege):
        if not isinstance(privilege, basestring):
            try:
                privilege = privilege.name
            except AttributeError:
                # It's a Need
                try:
                    privilege = privilege.value
                except AttributeError:
                    raise
        return self.filter(Privilege.name == privilege).first()


class Privilege(db.Model):
    __tablename__   = 'privileges'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(50), nullable=False, unique=True)

    query_class     = PrivilegeQuery

    def __init__(self, privilege_name):
        if not isinstance(privilege_name, basestring):
            try:
                privilege_name = privilege_name.name
            except AttributeError:
                # It's a Need
                try:
                    privilege_name = privilege_name.need
                except AttributeError:
                    raise
        self.name = privilege_name

    def __repr__(self):
        return '<{0} {1!r}>'.format(self.__class__.__name__, self.name)


# Association table
account_privileges = db.Table(
    'account_privileges', db.metadata,
    db.Column('account_github_id', db.Integer, db.ForeignKey('accounts.github_id'), nullable=False),
    db.Column('privilege_id', db.Integer, db.ForeignKey('privileges.id'), nullable=False)
)
# <---- Define the Models ------------------------------------------------------------------------
