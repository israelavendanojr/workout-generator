"""Add type to Exercise

Revision ID: 5f1e20bb9db0
Revises: 3a0dff74ce0c
Create Date: 2025-04-23 17:56:14.649781

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f1e20bb9db0'
down_revision = '3a0dff74ce0c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exercise', schema=None) as batch_op:
        batch_op.add_column(sa.Column('type', sa.Enum('COMPOUND', 'ISOLATION', name='exercise_type_enum'), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('exercise', schema=None) as batch_op:
        batch_op.drop_column('type')

    # ### end Alembic commands ###
