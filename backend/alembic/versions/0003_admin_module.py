"""admin module

Revision ID: 0003_admin_module
Revises: 0002_auth_sessions
Create Date: 2026-07-02
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_admin_module"
down_revision = "0002_auth_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "teacher_class_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("teacher_id", sa.Integer(), sa.ForeignKey("teachers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("class_id", sa.Integer(), sa.ForeignKey("school_classes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subjects.id", ondelete="SET NULL")),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("teacher_id", "class_id", "subject_id", name="uq_teacher_class_subject"),
    )
    op.create_index("ix_teacher_class_assignments_teacher_id", "teacher_class_assignments", ["teacher_id"])
    op.create_index("ix_teacher_class_assignments_class_id", "teacher_class_assignments", ["class_id"])

    op.create_table(
        "school_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("key", name="uq_school_settings_key"),
    )
    op.create_index("ix_school_settings_key", "school_settings", ["key"])


def downgrade() -> None:
    op.drop_index("ix_school_settings_key", table_name="school_settings")
    op.drop_table("school_settings")
    op.drop_index("ix_teacher_class_assignments_class_id", table_name="teacher_class_assignments")
    op.drop_index("ix_teacher_class_assignments_teacher_id", table_name="teacher_class_assignments")
    op.drop_table("teacher_class_assignments")
