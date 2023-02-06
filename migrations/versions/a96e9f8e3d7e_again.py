"""again

Revision ID: a96e9f8e3d7e
Revises: c2bd47ada44d
Create Date: 2023-01-30 09:09:01.077247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a96e9f8e3d7e'
down_revision = 'c2bd47ada44d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('staff_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('staff_id')

    # ### end Alembic commands ###