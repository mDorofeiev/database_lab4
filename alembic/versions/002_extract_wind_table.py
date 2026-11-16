"""002_extract_wind_table

Revision ID: 002_extract_wind
Revises: 001_initial
Create Date: 2026-11-08 11:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "002_extract_wind"
down_revision = "001_initial"
branch_labels = None
depends_on = None

wind_direction_enum = sa.Enum(
    "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
    "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    name="wind_direction_enum",
    create_type=False
)

def upgrade() -> None:
    # Таблиця для параметрів вітру
    op.create_table(
        "wind_info",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "weather_report_id",
            sa.Integer(),
            sa.ForeignKey("weather_reports.id", ondelete="CASCADE"),
            nullable=False,
            unique=True
        ),
        sa.Column("wind_mph", sa.Float(), nullable=False),
        sa.Column("wind_kph", sa.Float(), nullable=False),
        sa.Column("wind_degree", sa.Integer(), nullable=False),
        sa.Column("wind_direction", wind_direction_enum, nullable=False),
        sa.Column("gust_mph", sa.Float(), nullable=False),
        sa.Column("gust_kph", sa.Float(), nullable=False),
    )

    # Перенесення вже існуючих даних без втрат із weather_reports у wind_info
    op.execute(
        """
        INSERT INTO wind_info (
            weather_report_id, wind_mph, wind_kph, wind_degree, wind_direction, gust_mph, gust_kph
        )
        SELECT id, wind_mph, wind_kph, wind_degree, wind_direction, gust_mph, gust_kph
        FROM weather_reports
        """
    )

    # Видалення старих колонок вітру з основної таблиці
    with op.batch_alter_table("weather_reports") as batch_op:
        batch_op.drop_column("wind_mph")
        batch_op.drop_column("wind_kph")
        batch_op.drop_column("wind_degree")
        batch_op.drop_column("wind_direction")
        batch_op.drop_column("gust_mph")
        batch_op.drop_column("gust_kph")

def downgrade() -> None:
    # Повернення колонок у таблицю weather_reports (NULLABLE для уникнення проблем із даними)
    with op.batch_alter_table("weather_reports") as batch_op:
        batch_op.add_column(sa.Column("wind_mph", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("wind_kph", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("wind_degree", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("wind_direction", wind_direction_enum, nullable=True))
        batch_op.add_column(sa.Column("gust_mph", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("gust_kph", sa.Float(), nullable=True))

    # Відновлення даних з wind_info назад у weather_reports
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            UPDATE weather_reports wr
            SET wind_mph = wi.wind_mph,
                wind_kph = wi.wind_kph,
                wind_degree = wi.wind_degree,
                wind_direction = wi.wind_direction,
                gust_mph = wi.gust_mph,
                gust_kph = wi.gust_kph
            FROM wind_info wi
            WHERE wr.id = wi.weather_report_id
            """
        )
    else:
        op.execute(
            """
            UPDATE weather_reports wr
            INNER JOIN wind_info wi ON wr.id = wi.weather_report_id
            SET wr.wind_mph = wi.wind_mph,
                wr.wind_kph = wi.wind_kph,
                wr.wind_degree = wi.wind_degree,
                wr.wind_direction = wi.wind_direction,
                wr.gust_mph = wi.gust_mph,
                wr.gust_kph = wi.gust_kph
            """
        )

    # Знову NOT NULL та видалення таблиці wind_info
    with op.batch_alter_table("weather_reports") as batch_op:
        batch_op.alter_column("wind_mph", existing_type=sa.Float(), nullable=False)
        batch_op.alter_column("wind_kph", existing_type=sa.Float(), nullable=False)
        batch_op.alter_column("wind_degree", existing_type=sa.Integer(), nullable=False)
        batch_op.alter_column("wind_direction", existing_type=wind_direction_enum, nullable=False)
        batch_op.alter_column("gust_mph", existing_type=sa.Float(), nullable=False)
        batch_op.alter_column("gust_kph", existing_type=sa.Float(), nullable=False)

    op.drop_table("wind_info")