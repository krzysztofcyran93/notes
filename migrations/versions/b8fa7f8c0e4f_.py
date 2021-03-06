"""empty message

Revision ID: b8fa7f8c0e4f
Revises: c4ce55a48fca
Create Date: 2020-03-09 20:32:42.585296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b8fa7f8c0e4f'
down_revision = 'c4ce55a48fca'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('department', sa.Column('user_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'department', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'department', type_='foreignkey')
    op.drop_column('department', 'user_id')
    # ### end Alembic commands ###
