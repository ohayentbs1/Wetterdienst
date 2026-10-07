"""Add DWD daily weather data

Revision ID: 2bfef0c42d6a
Revises: e5ecf1864289
Create Date: 2026-10-07 21:08:52

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2bfef0c42d6a'
down_revision = 'e5ecf1864289'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'weather_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('STATIONS_ID', sa.Integer(), nullable=False),
        sa.Column('MESS_DATUM', sa.Date(), nullable=False),
        sa.Column('QN_3', sa.Integer(), nullable=True),
        sa.Column('FX', sa.Float(), nullable=True),
        sa.Column('FM', sa.Float(), nullable=True),
        sa.Column('QN_4', sa.Integer(), nullable=True),
        sa.Column('RSK', sa.Float(), nullable=True),
        sa.Column('RSKF', sa.Integer(), nullable=True),
        sa.Column('SDK', sa.Float(), nullable=True),
        sa.Column('SHK_TAG', sa.Integer(), nullable=True),
        sa.Column('NM', sa.Float(), nullable=True),
        sa.Column('VPM', sa.Float(), nullable=True),
        sa.Column('PM', sa.Float(), nullable=True),
        sa.Column('TMK', sa.Float(), nullable=True),
        sa.Column('UPM', sa.Float(), nullable=True),
        sa.Column('TXK', sa.Float(), nullable=True),
        sa.Column('TNK', sa.Float(), nullable=True),
        sa.Column('TGK', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['STATIONS_ID'], ['station.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint(
            'STATIONS_ID',
            'MESS_DATUM',
            name='uq_weather_data_station_date',
        ),
    )


def downgrade():
    op.drop_table('weather_data')
