"""Add plan column to SavedPlan

Revision ID: 3d6605fedb7d
Revises: 882df195d237
Create Date: 2025-04-27 14:16:33.202410

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3d6605fedb7d'
down_revision = '882df195d237'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_plan', schema=None) as batch_op:
        batch_op.add_column(sa.Column('plan', sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('saved_plan', schema=None) as batch_op:
        batch_op.drop_column('plan')

    # ### end Alembic commands ###
