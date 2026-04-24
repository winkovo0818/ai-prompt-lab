"""Prompt Commit Model"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class PromptCommit(SQLModel, table=True):
    """Prompt 版本提交"""
    __tablename__ = "prompt_commit"

    id: int = Field(primary_key=True, autoincrement=True)
    branch_id: int = Field(foreign_key="prompt_branch.id", nullable=False, index=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="prompt_commit.id")
    title: str = Field(max_length=255, nullable=False)
    content: str = Field(nullable=False)
    variables_schema: Optional[dict] = Field(default=None)
    created_by: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships (defined in branch.py to avoid circular imports)
    # branch: PromptBranch = Relationship(back_populates="commits")
    # parent: Optional[PromptCommit] = Relationship()


from app.models.branch import PromptBranch