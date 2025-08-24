"""Tabela de artefatos e eventos."""
from alembic import op
import sqlalchemy as sa

revision = '2025_08_23'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'artifacts',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('path', sa.String(), nullable=False),
    )
    op.create_table(
        'artifact_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('artifact_id', sa.String(), nullable=False),
        sa.Column('event', sa.String(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('artifact_events')
    op.drop_table('artifacts')
