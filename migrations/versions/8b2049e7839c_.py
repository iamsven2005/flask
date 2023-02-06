"""empty message

Revision ID: 8b2049e7839c
Revises: 51f04761f6a8
Create Date: 2023-01-23 17:32:43.790670

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b2049e7839c'
down_revision = '51f04761f6a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('None', type_='unique')
        batch_op.drop_column('retailer_id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('retailer_id', sa.INTEGER(), nullable=True))
        batch_op.create_unique_constraint('None', ['retailer_id'])

    # ### end Alembic commands ###
