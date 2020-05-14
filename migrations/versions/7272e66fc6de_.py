"""empty message

Revision ID: 7272e66fc6de
Revises: e7da4bb78850
Create Date: 2020-05-14 01:20:05.985933

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7272e66fc6de'
down_revision = 'e7da4bb78850'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('date_created', sa.DateTime(), nullable=False))
    op.add_column('Artist', sa.Column('date_updated', sa.DateTime(), nullable=False))
    op.add_column('Venue', sa.Column('date_created', sa.DateTime(), nullable=False))
    op.add_column('Venue', sa.Column('date_updated', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'date_updated')
    op.drop_column('Venue', 'date_created')
    op.drop_column('Artist', 'date_updated')
    op.drop_column('Artist', 'date_created')
    # ### end Alembic commands ###
