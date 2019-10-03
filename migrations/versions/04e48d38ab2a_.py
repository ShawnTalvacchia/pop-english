"""empty message

Revision ID: 04e48d38ab2a
Revises: ced7e0afd6b7
Create Date: 2019-09-30 16:27:09.117131

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04e48d38ab2a'
down_revision = 'ced7e0afd6b7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('module', sa.Column('end_date', sa.String(length=256), nullable=True))
    op.add_column('module', sa.Column('start_date', sa.String(length=256), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('module', 'start_date')
    op.drop_column('module', 'end_date')
    # ### end Alembic commands ###