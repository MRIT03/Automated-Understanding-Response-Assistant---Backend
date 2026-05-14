"""add recording_path to incidents

Revision ID: 0002_add_recording_path
Revises: deaebcc97667_align_schema_to_sql
Create Date: 2026-05-10
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_add_recording_path"
down_revision = "deaebcc97667"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "incidents",
        sa.Column("recording_path", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("incidents", "recording_path")
