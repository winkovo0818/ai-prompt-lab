"""Add prompt test suite tables

Revision ID: 20260427_prompt_tests
Revises: xxx
Create Date: 2026-04-27
"""
from alembic import op
import sqlalchemy as sa


revision = "20260427_prompt_tests"
down_revision = "xxx"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "prompt_test_suites",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("prompt_id", sa.Integer(), sa.ForeignKey("prompts.id"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("suite_type", sa.String(20), nullable=False, default="smoke"),
        sa.Column("is_active", sa.Boolean(), nullable=False, default=True),
        sa.Column("auto_run_on_save", sa.Boolean(), nullable=False, default=False),
        sa.Column("baseline_mode", sa.String(50), nullable=False, default="previous_version"),
        sa.Column("fixed_baseline_version", sa.Integer(), nullable=True),
        sa.Column("test_cases", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_prompt_test_suites_user_id", "prompt_test_suites", ["user_id"])
    op.create_index("ix_prompt_test_suites_prompt_id", "prompt_test_suites", ["prompt_id"])

    op.create_table(
        "prompt_test_runs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("suite_id", sa.Integer(), sa.ForeignKey("prompt_test_suites.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("prompt_id", sa.Integer(), sa.ForeignKey("prompts.id"), nullable=False),
        sa.Column("candidate_version", sa.Integer(), nullable=False),
        sa.Column("baseline_version", sa.Integer(), nullable=True),
        sa.Column("trigger_source", sa.String(50), nullable=False, default="manual"),
        sa.Column("status", sa.String(50), nullable=False, default="pending"),
        sa.Column("summary", sa.JSON(), nullable=False),
        sa.Column("results", sa.JSON(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_prompt_test_runs_suite_id", "prompt_test_runs", ["suite_id"])
    op.create_index("ix_prompt_test_runs_user_id", "prompt_test_runs", ["user_id"])
    op.create_index("ix_prompt_test_runs_prompt_id", "prompt_test_runs", ["prompt_id"])
    op.create_index("ix_prompt_test_runs_candidate_version", "prompt_test_runs", ["candidate_version"])
    op.create_index("ix_prompt_test_runs_baseline_version", "prompt_test_runs", ["baseline_version"])


def downgrade():
    op.drop_index("ix_prompt_test_runs_baseline_version", table_name="prompt_test_runs")
    op.drop_index("ix_prompt_test_runs_candidate_version", table_name="prompt_test_runs")
    op.drop_index("ix_prompt_test_runs_prompt_id", table_name="prompt_test_runs")
    op.drop_index("ix_prompt_test_runs_user_id", table_name="prompt_test_runs")
    op.drop_index("ix_prompt_test_runs_suite_id", table_name="prompt_test_runs")
    op.drop_table("prompt_test_runs")
    op.drop_index("ix_prompt_test_suites_prompt_id", table_name="prompt_test_suites")
    op.drop_index("ix_prompt_test_suites_user_id", table_name="prompt_test_suites")
    op.drop_table("prompt_test_suites")
