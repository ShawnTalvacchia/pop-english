"""empty message

Revision ID: 3905613b8d60
Revises: cfddac12c7d1
Create Date: 2019-09-26 19:51:31.870613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3905613b8d60'
down_revision = 'cfddac12c7d1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profile', sa.Column('img', sa.String(length=2500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('profile', 'img')
    # ### end Alembic commands ###
