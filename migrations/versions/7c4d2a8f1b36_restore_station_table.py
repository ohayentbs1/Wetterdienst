"""Restore station table

Revision ID: 7c4d2a8f1b36
Revises: 2bfef0c42d6a
Create Date: 2026-10-07

"""
from alembic import op
import sqlalchemy as sa


revision = '7c4d2a8f1b36'
down_revision = '2bfef0c42d6a'
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
        sa.Column('abgabe', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('station')
