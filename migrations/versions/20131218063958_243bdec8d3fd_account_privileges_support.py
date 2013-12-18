'''
    Account Privileges Support


    :copyright: (C) 2013 by the SaltStack Team, see AUTHORS for more details.
    :license: Apache 2.0, see LICENSE for more details.


    Revision ID: 243bdec8d3fd
    Revises: 1d780a757476
    Create Date: 2013-12-18 06:39:58.290749

'''

# revision identifiers, used by Alembic.
revision = '243bdec8d3fd'
down_revision = '1d780a757476'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('privileges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('account_privileges',
        sa.Column('account_github_id', sa.Integer(), nullable=False),
        sa.Column('privilege_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['account_github_id'], ['accounts.github_id']),
        sa.ForeignKeyConstraint(['privilege_id'], ['privileges.id']),
        sa.PrimaryKeyConstraint()
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('account_privileges')
    op.drop_table('privileges')
    ### end Alembic commands ###
