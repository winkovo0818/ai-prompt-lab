"""Prompt Pull Request Model"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class PromptPullRequest(SQLModel, table=True):
    """Prompt Pull Request"""
    __tablename__ = "prompt_pull_request"

    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompts.id", nullable=False, index=True)
    source_branch_id: int = Field(foreign_key="prompt_branch.id", nullable=False)
    target_branch_id: int = Field(foreign_key="prompt_branch.id", nullable=False)
    title: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="open")  # open, merged, closed
    author_id: int = Field(foreign_key="user.id", nullable=False)
    reviewer_id: Optional[int] = Field(default=None, foreign_key="user.id")
    merged_by: Optional[int] = Field(default=None, foreign_key="user.id")
    merged_at: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    source_branch: "PromptBranch" = Relationship(back_populates="source_prs")
    target_branch: "PromptBranch" = Relationship(back_populates="target_prs")