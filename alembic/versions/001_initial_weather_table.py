"""001_initial_weather_table

Revision ID: 001_initial
Revises: 
Create Date: 2026-11-08 10:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None

wind_direction_enum = sa.Enum(
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    name="wind_direction_enum"
)

def upgrade() -> None:
    op.create_table(
        "weather_reports",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("country", sa.String(length=100), nullable=False, index=True),
        sa.Column("location_name", sa.String(length=100), nullable=False, index=True),
        sa.Column("temperature_celsius", sa.Float(), nullable=False),
        sa.Column("last_updated", sa.Date(), nullable=False, index=True),
        sa.Column("sunrise", sa.Time(), nullable=False),
        sa.Column("wind_mph", sa.Float(), nullable=False),
        sa.Column("wind_kph", sa.Float(), nullable=False),
        sa.Column("wind_degree", sa.Integer(), nullable=False),
        sa.Column("wind_direction", wind_direction_enum, nullable=False),
        sa.Column("gust_mph", sa.Float(), nullable=False),
        sa.Column("gust_kph", sa.Float(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table("weather_reports")
    wind_direction_enum.drop(op.get_bind(), checkfirst=True)