"""Initial schema

Revision ID: 649889d97fa2
Revises: 
Create Date: 2026-10-05 12:23:32.796613

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '649889d97fa2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'station',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('von_datum', sa.Date(), nullable=True),
        sa.Column('bis_datum', sa.Date(), nullable=True),
        sa.Column('stationshoehe', sa.Integer(), nullable=True),
        sa.Column('geo_breite', sa.Float(), nullable=True),
        sa.Column('geo_laenge', sa.Float(), nullable=True),
        sa.Column('stationsname', sa.String(length=100), nullable=True),
        sa.Column('bundesland', sa.String(length=100), nullable=True),
        sa.Column('abgabe', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'wetter_eintrag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stadt', sa.String(length=100), nullable=False),
        sa.Column('temperatur', sa.Float(), nullable=False),
        sa.Column('beschreibung', sa.String(length=200), nullable=True),
        sa.Column('zeitstempel', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('wetter_eintrag')
    op.drop_table('station')
