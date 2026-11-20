"""migrate review history to SM-2 state

Revision ID: 9d2f84a71c1b
Revises: 5fd5c41a9dbe
"""

from alembic import op
import sqlalchemy as sa


revision = "9d2f84a71c1b"
down_revision = "5fd5c41a9dbe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("review_history", sa.Column("quality", sa.Integer(), nullable=True))
    op.add_column(
        "review_history",
        sa.Column("repetitions", sa.Integer(), nullable=False, server_default="0"),
    )
    op.execute(
        "UPDATE review_history "
        "SET quality = CASE WHEN was_correct THEN 5 ELSE 2 END"
    )
    op.alter_column("review_history", "quality", nullable=False)
    op.alter_column(
        "review_history",
        "ease_factor",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=True,
        nullable=False,
        postgresql_using=(
            "CASE WHEN ease_factor > 10 THEN ease_factor::double precision / 100.0 "
            "ELSE ease_factor::double precision END"
        ),
    )
    op.alter_column("review_history", "interval", existing_type=sa.Integer(), nullable=False)
    op.alter_column("review_history", "timestamp", existing_type=sa.DateTime(), nullable=False)
    op.alter_column("review_history", "repetitions", server_default=None)


def downgrade() -> None:
    op.alter_column("review_history", "timestamp", existing_type=sa.DateTime(), nullable=True)
    op.alter_column("review_history", "interval", existing_type=sa.Integer(), nullable=True)
    op.alter_column(
        "review_history",
        "ease_factor",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=False,
        nullable=True,
        postgresql_using="round(ease_factor * 100)::integer",
    )
    op.drop_column("review_history", "repetitions")
    op.drop_column("review_history", "quality")
