from datetime import datetime
from typing import Dict, List, Optional

from sqlmodel import Column, Field, JSON, SQLModel, Text


class PromptTestSuite(SQLModel, table=True):
    """Reusable test suite attached to a Prompt."""

    __tablename__ = "prompt_test_suites"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    prompt_id: int = Field(foreign_key="prompts.id", index=True)

    name: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    suite_type: str = Field(default="smoke", max_length=20)  # smoke | full
    is_active: bool = Field(default=True)
    auto_run_on_save: bool = Field(default=False)
    baseline_mode: str = Field(default="previous_version", max_length=50)
    fixed_baseline_version: Optional[int] = Field(default=None)
    test_cases: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PromptTestRun(SQLModel, table=True):
    """Single execution result for a Prompt test suite."""

    __tablename__ = "prompt_test_runs"

    id: Optional[int] = Field(default=None, primary_key=True)
    suite_id: int = Field(foreign_key="prompt_test_suites.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    prompt_id: int = Field(foreign_key="prompts.id", index=True)

    candidate_version: int = Field(index=True)
    baseline_version: Optional[int] = Field(default=None, index=True)
    trigger_source: str = Field(default="manual", max_length=50)  # manual | save
    status: str = Field(default="pending", max_length=50)
    summary: Dict = Field(default_factory=dict, sa_column=Column(JSON))
    results: List[Dict] = Field(default_factory=list, sa_column=Column(JSON))
    error: Optional[str] = Field(default=None, sa_column=Column(Text))

    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class PromptTestSuiteCreate(SQLModel):
    prompt_id: int
    name: str
    description: Optional[str] = None
    suite_type: str = "smoke"
    is_active: bool = True
    auto_run_on_save: bool = False
    baseline_mode: str = "previous_version"
    fixed_baseline_version: Optional[int] = None
    test_cases: List[Dict] = Field(default_factory=list)


class PromptTestSuiteUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    suite_type: Optional[str] = None
    is_active: Optional[bool] = None
    auto_run_on_save: Optional[bool] = None
    baseline_mode: Optional[str] = None
    fixed_baseline_version: Optional[int] = None
    test_cases: Optional[List[Dict]] = None


class PromptTestRunRequest(SQLModel):
    candidate_version: Optional[int] = None
    baseline_version: Optional[int] = None
    trigger_source: str = "manual"
    model: Optional[str] = None
    temperature: float = 0.0
    enable_evaluation: bool = True
