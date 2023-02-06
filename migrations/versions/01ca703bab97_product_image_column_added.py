"""product image column added

Revision ID: 01ca703bab97
Revises: d69b1eb487a0
Create Date: 2023-02-05 23:14:14.565529

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01ca703bab97'
down_revision = 'd69b1eb487a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item__img',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('img', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('item__img')
    # ### end Alembic commands ###