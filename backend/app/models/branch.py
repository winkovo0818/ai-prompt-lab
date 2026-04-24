"""Prompt Branch Model"""
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from app.models.user import User


class PromptBranch(SQLModel, table=True):
    """Prompt 分支"""
    __tablename__ = "prompt_branch"

    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: int = Field(foreign_key="prompt.id", nullable=False, index=True)
    name: str = Field(max_length=100, nullable=False)
    description: Optional[str] = Field(default=None)
    base_branch_id: Optional[int] = Field(default=None, foreign_key="prompt_branch.id")
    is_default: bool = Field(default=False)
    created_by: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    prompt: "Prompt" = Relationship(back_populates="branches")
    commits: list["PromptCommit"] = Relationship(back_populates="branch", cascade_delete=True)
    source_prs: list["PromptPullRequest"] = Relationship(
        back_populates="source_branch",
        foreign_keys="PromptPullRequest.source_branch_id"
    )
    target_prs: list["PromptPullRequest"] = Relationship(
        back_populates="target_branch",
        foreign_keys="PromptPullRequest.target_branch_id"
    )


from app.models.prompt import Prompt
from app.models.commit import PromptCommit
from app.models.pull_request import PromptPullRequest