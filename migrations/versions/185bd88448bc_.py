"""empty message

Revision ID: 185bd88448bc
Revises: 04e48d38ab2a
Create Date: 2019-09-30 16:59:49.704777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '185bd88448bc'
down_revision = '04e48d38ab2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('module', sa.Column('default_img', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('module', 'default_img')
    # ### end Alembic commands ###
