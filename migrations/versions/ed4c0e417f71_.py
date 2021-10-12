"""empty message

Revision ID: ed4c0e417f71
Revises: 
Create Date: 2021-10-12 21:04:34.189714

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ed4c0e417f71'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('persons',
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=100), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.Column('gender', sa.String(length=30), nullable=False),
    sa.Column('birthday', sa.Date(), nullable=False),
    sa.Column('address', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('person_id')
    )
    op.create_table('emails',
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('email_type', sa.String(length=30), nullable=False),
    sa.Column('email_address', sa.String(length=254), nullable=False),
    sa.ForeignKeyConstraint(['person_id'], ['persons.person_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('email_address')
    )
    op.create_table('phones',
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('phone_type', sa.String(length=30), nullable=False),
    sa.Column('phone_number', sa.String(length=30), nullable=False),
    sa.ForeignKeyConstraint(['person_id'], ['persons.person_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('phone_number')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('phones')
    op.drop_table('emails')
    op.drop_table('persons')
    # ### end Alembic commands ###
