"""003_add_should_go_outside

Revision ID: 003_should_go_outside
Revises: 002_extract_wind
Create Date: 2026-11-08 12:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "003_should_go_outside"
down_revision = "002_extract_wind"
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Додавання колонки (спочатку дозвіл NULL, щоб уникнути проблем із вже існуючими рядками)
    op.add_column(
        "wind_info",
        sa.Column(
            "should_go_outside",
            sa.Boolean(),
            nullable=True,
            server_default=sa.true()
        )
    )

    # Обчислення значення для вже існуючих рядків за формулою: вітер <= 36 км/год та пориви <= 50 км/год
    op.execute(
        """
        UPDATE wind_info
        SET should_go_outside = CASE
            WHEN wind_kph <= 36.0 AND gust_kph <= 50.0 THEN TRUE
            ELSE FALSE
        END
        """
    )

    # Заборона NULL
    with op.batch_alter_table("wind_info") as batch_op:
        batch_op.alter_column(
            "should_go_outside",
            existing_type=sa.Boolean(),
            nullable=False
        )

def downgrade() -> None:
    with op.batch_alter_table("wind_info") as batch_op:
        batch_op.drop_column("should_go_outside")