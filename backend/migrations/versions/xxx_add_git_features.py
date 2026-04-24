"""Add git features: branch, commit, pull_request tables

Revision ID: xxx
Revises:
Create Date: 2026-04-24
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'xxx'
down_revision = None  # TODO: set to last migration
branch_labels = None
depends_on = None


def upgrade():
    # Add default_branch_id to prompt table
    op.add_column('prompt', sa.Column('default_branch_id', sa.Integer(), nullable=True))
    op.create_index('idx_prompt_default_branch', 'prompt', ['default_branch_id'])

    # Create prompt_branch table
    op.create_table(
        'prompt_branch',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('prompt_id', sa.Integer(), sa.ForeignKey('prompt.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('base_branch_id', sa.Integer(), sa.ForeignKey('prompt_branch.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_default', sa.Boolean(), default=False),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_branch_prompt', 'prompt_branch', ['prompt_id', 'is_default'])
    op.create_unique_constraint('uk_prompt_branch', 'prompt_branch', ['prompt_id', 'name'])

    # Create prompt_commit table
    op.create_table(
        'prompt_commit',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('branch_id', sa.Integer(), sa.ForeignKey('prompt_branch.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_id', sa.Integer(), sa.ForeignKey('prompt_commit.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('variables_schema', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('idx_commit_branch_time', 'prompt_commit', ['branch_id', 'created_at'])

    # Create prompt_pull_request table
    op.create_table(
        'prompt_pull_request',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('prompt_id', sa.Integer(), sa.ForeignKey('prompt.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_branch_id', sa.Integer(), sa.ForeignKey('prompt_branch.id'), nullable=False),
        sa.Column('target_branch_id', sa.Integer(), sa.ForeignKey('prompt_branch.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('open', 'merged', 'closed', name='pr_status'), default='open'),
        sa.Column('author_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('merged_by', sa.Integer(), sa.ForeignKey('user.id'), nullable=True),
        sa.Column('merged_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('idx_pr_prompt_status', 'prompt_pull_request', ['prompt_id', 'status'])


def downgrade():
    op.drop_index('idx_pr_prompt_status', table_name='prompt_pull_request')
    op.drop_table('prompt_pull_request')
    op.drop_index('idx_commit_branch_time', table_name='prompt_commit')
    op.drop_table('prompt_commit')
    op.drop_index('idx_branch_prompt', table_name='prompt_branch')
    op.drop_table('prompt_branch')
    op.drop_index('idx_prompt_default_branch', table_name='prompt')
    op.drop_column('prompt', 'default_branch_id')