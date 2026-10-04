"""Create the notes table."""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("text", sa.String(500), nullable=False),
        sa.CheckConstraint("length(trim(text)) > 0", name="notes_text_not_blank"),
    )


def downgrade() -> None:
    op.drop_table("notes")
