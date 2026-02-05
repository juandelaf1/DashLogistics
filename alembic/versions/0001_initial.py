"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-02-05 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create shipping_stats example table
    op.create_table(
        'shipping_stats',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('origin', sa.String(length=128), nullable=False),
        sa.Column('destination', sa.String(length=128), nullable=False),
        sa.Column('weight', sa.Float, nullable=True),
        sa.Column('date', sa.Date, nullable=True),
        sa.Column('pipeline_run_id', sa.String(length=64), nullable=True),
    )

    # Create master_shipping_data table
    op.create_table(
        'master_shipping_data',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('state', sa.String(length=64), nullable=False),
        sa.Column('population', sa.Integer, nullable=True),
        sa.Column('diesel_price', sa.Float, nullable=True),
        sa.Column('current_temp', sa.Float, nullable=True),
    )

    # Create fuel_prices
    op.create_table(
        'fuel_prices',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('state', sa.String(length=64), nullable=False),
        sa.Column('diesel_price', sa.Float, nullable=True),
        sa.Column('updated_at', sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table('fuel_prices')
    op.drop_table('master_shipping_data')
    op.drop_table('shipping_stats')
