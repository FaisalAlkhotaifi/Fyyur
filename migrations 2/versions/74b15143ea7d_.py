"""empty message

Revision ID: 74b15143ea7d
Revises: 8556a7d5e5f9
Create Date: 2020-05-14 04:42:12.284196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74b15143ea7d'
down_revision = '8556a7d5e5f9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('artist_id', sa.Integer(), nullable=True))
    op.add_column('Show', sa.Column('venue_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'venue_id')
    op.drop_column('Show', 'artist_id')
    # ### end Alembic commands ###
