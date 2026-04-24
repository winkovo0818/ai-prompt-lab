"""Prompt Commit Model"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON


class PromptCommit(SQLModel, table=True):
    """Prompt 版本提交"""
    __tablename__ = "prompt_commit"

    id: Optional[int] = Field(default=None, primary_key=True)
    branch_id: int = Field(foreign_key="prompt_branch.id", nullable=False, index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="prompt_commit.id")
    title: str = Field(max_length=255, nullable=False)
    content: str = Field(nullable=False)
    variables_schema: Optional[dict] = Field(default=None, sa_type=JSON)
    created_by: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (defined in branch.py to avoid circular imports)
    # branch: PromptBranch = Relationship(back_populates="commits")
    # parent: Optional[PromptCommit] = Relationship()


from app.models.branch import PromptBranch