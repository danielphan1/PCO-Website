"""Initial schema -- all 7 tables with seed data

Revision ID: 001
Revises:
Create Date: 2026-03-03
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False, server_default="member"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. refresh_tokens
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"], unique=True)

    # 3. interest_submissions
    op.create_table(
        "interest_submissions",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("phone", sa.String(), nullable=False),
        sa.Column("year", sa.String(), nullable=False),
        sa.Column("major", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_interest_submissions_email", "interest_submissions", ["email"], unique=True)

    # 4. events (event PDFs)
    op.create_table(
        "events",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("storage_path", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("uploaded_by", sa.UUID(), sa.ForeignKey("users.id"), nullable=True),
    )

    # 5. rush_info (single-row table)
    op.create_table(
        "rush_info",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("dates", sa.Text(), nullable=False, server_default=""),
        sa.Column("times", sa.Text(), nullable=False, server_default=""),
        sa.Column("locations", sa.Text(), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("is_published", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # 6. org_content (one row per section)
    op.create_table(
        "org_content",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("section", sa.String(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_org_content_section", "org_content", ["section"], unique=True)

    # 7. audit_log
    op.create_table(
        "audit_log",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("actor_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("target_id", sa.UUID(), nullable=True),
        sa.Column("target_type", sa.String(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # Seed data

    # One unpublished rush_info row
    op.execute(
        sa.text(
            "INSERT INTO rush_info "
            "(id, dates, times, locations, description, is_published, updated_at) "
            "VALUES (gen_random_uuid(), '', '', '', '', false, now())"
        )
    )

    # Three org_content rows (empty content)
    for section in ("history", "philanthropy", "contacts"):
        op.execute(
            sa.text(
                "INSERT INTO org_content (id, section, content, updated_at) "
                "VALUES (gen_random_uuid(), :section, '', now())"
            ).bindparams(section=section)
        )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_index("ix_org_content_section", "org_content")
    op.drop_table("org_content")
    op.drop_table("rush_info")
    op.drop_table("events")
    op.drop_index("ix_interest_submissions_email", "interest_submissions")
    op.drop_table("interest_submissions")
    op.drop_index("ix_refresh_tokens_token_hash", "refresh_tokens")
    op.drop_table("refresh_tokens")
    op.drop_index("ix_users_email", "users")
    op.drop_table("users")
