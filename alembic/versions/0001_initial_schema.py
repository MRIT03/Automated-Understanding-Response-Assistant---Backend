"""initial schema

Revision ID: 0001_initial_schema
Revises: None
Create Date: 2026-03-30 00:00:00
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    incident_status = sa.Enum(
        "reported",
        "dispatched",
        "en_route",
        "on_scene",
        "contained",
        "resolved",
        "closed",
        name="incidentstatus",
    )
    call_status = sa.Enum(
        "received",
        "triaged",
        "dispatched",
        "closed",
        "cancelled",
        name="callstatus",
    )
    priority = sa.Enum("low", "medium", "high", "critical", name="prioritylevel")

    incident_status.create(op.get_bind(), checkfirst=True)
    call_status.create(op.get_bind(), checkfirst=True)
    priority.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "dispatchers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("badge_number", sa.String(length=50), nullable=False),
        sa.Column("phone_number", sa.String(length=30), nullable=True),
        sa.Column("shift_name", sa.String(length=100), nullable=True),
        sa.Column("rank", sa.String(length=100), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("badge_number"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )

    op.create_table(
        "incident_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_priority", priority, nullable=False, server_default="medium"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("incident_number", sa.String(length=50), nullable=False),
        sa.Column("incident_type_id", sa.Integer(), nullable=False),
        sa.Column("status", incident_status, nullable=False, server_default="reported"),
        sa.Column("priority", priority, nullable=False, server_default="medium"),
        sa.Column("location_address", sa.String(length=255), nullable=False),
        sa.Column("location_details", sa.Text(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("units_requested", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("units_dispatched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["incident_type_id"], ["incident_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("incident_number"),
    )

    op.create_table(
        "calls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("call_reference", sa.String(length=50), nullable=False),
        sa.Column("dispatcher_id", sa.Integer(), nullable=False),
        sa.Column("incident_id", sa.Integer(), nullable=True),
        sa.Column("caller_name", sa.String(length=255), nullable=True),
        sa.Column("caller_phone", sa.String(length=30), nullable=True),
        sa.Column("callback_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("source_channel", sa.String(length=50), nullable=False, server_default="phone"),
        sa.Column("call_status", call_status, nullable=False, server_default="received"),
        sa.Column("priority", priority, nullable=False, server_default="medium"),
        sa.Column("reported_location", sa.String(length=255), nullable=False),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("dispatcher_notes", sa.Text(), nullable=True),
        sa.Column("recording_url", sa.String(length=500), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["dispatcher_id"], ["dispatchers.id"]),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("call_reference"),
    )


def downgrade() -> None:
    op.drop_table("calls")
    op.drop_table("incidents")
    op.drop_table("incident_types")
    op.drop_table("dispatchers")

    sa.Enum(name="prioritylevel").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="callstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="incidentstatus").drop(op.get_bind(), checkfirst=True)
