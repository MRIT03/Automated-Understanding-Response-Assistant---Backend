"""add app settings table

Revision ID: 20260513_add_app_settings
Revises: PUT_YOUR_PREVIOUS_REVISION_ID_HERE
Create Date: 2026-05-13
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260513_add_app_settings"
down_revision = "0002_add_recording_path"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("key", sa.String(length=100), primary_key=True, nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index(op.f("ix_app_settings_key"), "app_settings", ["key"], unique=False)

    op.bulk_insert(
        sa.table(
            "app_settings",
            sa.column("key", sa.String),
            sa.column("value", sa.String),
        ),
        [
            {"key": "performance", "value": "moderate"},
            {"key": "operator_name", "value": "Operator"},
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_app_settings_key"), table_name="app_settings")
    op.drop_table("app_settings")
