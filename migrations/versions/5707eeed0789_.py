"""empty message

Revision ID: 5707eeed0789
Revises: b7b9c660b8c2
Create Date: 2020-03-08 22:06:03.375055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5707eeed0789'
down_revision = 'b7b9c660b8c2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('department',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user_departments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['department.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('departments')
    op.drop_column('user_roles', 'department_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_roles', sa.Column('department_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_table('departments',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='departments_pkey'),
    sa.UniqueConstraint('name', name='departments_name_key')
    )
    op.drop_table('user_departments')
    op.drop_table('department')
    # ### end Alembic commands ###
