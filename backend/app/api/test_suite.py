from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, func, select

from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.test_suite import (
    PromptTestRun,
    PromptTestRunRequest,
    PromptTestSuite,
    PromptTestSuiteCreate,
    PromptTestSuiteUpdate,
)
from ..models.user import User
from ..services.test_runner_service import TestRunnerService
from ..utils.response import error_response, success_response
from .prompt import check_prompt_access


router = APIRouter(prefix="/api/test-suite", tags=["Prompt测试集"])


def dump_model(model):
    return model.model_dump(mode="json")


def validate_suite_type(suite_type: str) -> bool:
    return suite_type in {"smoke", "full"}


@router.get("/prompt/{prompt_id}", response_model=dict)
async def get_prompt_test_suites(
    prompt_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
):
    """Get reusable test suites for a Prompt."""
    try:
        prompt, _ = check_prompt_access(prompt_id, current_user, db, require_edit=True)
    except Exception as exc:
        return error_response(code=4001, message=str(exc))

    suites = db.exec(
        select(PromptTestSuite)
        .where(PromptTestSuite.prompt_id == prompt.id)
        .order_by(PromptTestSuite.created_at.desc())
    ).all()

    return success_response(data=[dump_model(suite) for suite in suites])


@router.post("", response_model=dict)
async def create_test_suite(
    suite_data: PromptTestSuiteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
):
    """Create a reusable test suite."""
    try:
        prompt, _ = check_prompt_access(
            suite_data.prompt_id, current_user, db, require_edit=True
        )
    except Exception as exc:
        return error_response(code=4001, message=str(exc))

    if not validate_suite_type(suite_data.suite_type):
        return error_response(code=4002, message="suite_type 仅支持 smoke 或 full")

    suite = PromptTestSuite(
        user_id=current_user.id,
        prompt_id=prompt.id,
        name=suite_data.name,
        description=suite_data.description,
        suite_type=suite_data.suite_type,
        is_active=suite_data.is_active,
        auto_run_on_save=suite_data.auto_run_on_save,
        baseline_mode=suite_data.baseline_mode,
        fixed_baseline_version=suite_data.fixed_baseline_version,
        test_cases=suite_data.test_cases,
    )
    db.add(suite)
    db.commit()
    db.refresh(suite)

    return success_response(data=dump_model(suite), message="测试集创建成功")


@router.put("/{suite_id}", response_model=dict)
async def update_test_suite(
    suite_id: int,
    suite_data: PromptTestSuiteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
):
    """Update a reusable test suite."""
    suite = db.get(PromptTestSuite, suite_id)
    if not suite:
        return error_response(code=4004, message="测试集不存在")

    try:
        check_prompt_access(suite.prompt_id, current_user, db, require_edit=True)
    except Exception as exc:
        return error_response(code=4001, message=str(exc))

    updates = suite_data.model_dump(exclude_unset=True)
    if "suite_type" in updates and not validate_suite_type(updates["suite_type"]):
        return error_response(code=4002, message="suite_type 仅支持 smoke 或 full")

    for key, value in updates.items():
        setattr(suite, key, value)
    suite.updated_at = datetime.utcnow()

    db.add(suite)
    db.commit()
    db.refresh(suite)

    return success_response(data=dump_model(suite), message="测试集更新成功")


@router.post("/{suite_id}/run", response_model=dict)
async def run_test_suite(
    suite_id: int,
    run_data: PromptTestRunRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
):
    """Run a test suite against a candidate prompt version."""
    suite = db.get(PromptTestSuite, suite_id)
    if not suite:
        return error_response(code=4004, message="测试集不存在")

    try:
        check_prompt_access(suite.prompt_id, current_user, db, require_edit=True)
        run = await TestRunnerService.run_suite(
            db=db,
            suite=suite,
            runner_user_id=current_user.id,
            candidate_version=run_data.candidate_version,
            baseline_version=run_data.baseline_version,
            trigger_source=run_data.trigger_source,
            model=run_data.model,
            temperature=run_data.temperature,
            enable_evaluation=run_data.enable_evaluation,
        )
    except Exception as exc:
        return error_response(code=4005, message=f"测试集运行失败: {str(exc)}")

    return success_response(data=dump_model(run), message="测试集运行完成")


@router.get("/runs/{run_id}", response_model=dict)
async def get_test_run_detail(
    run_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
):
    """Get a single test run detail."""
    run = db.get(PromptTestRun, run_id)
    if not run:
        return error_response(code=4004, message="测试运行记录不存在")

    try:
        check_prompt_access(run.prompt_id, current_user, db)
    except Exception as exc:
        return error_response(code=4001, message=str(exc))

    return success_response(data=dump_model(run))


@router.get("/runs", response_model=dict)
async def get_test_runs(
    prompt_id: Optional[int] = None,
    suite_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session),
):
    """List test run history."""
    statement = select(PromptTestRun).where(PromptTestRun.user_id == current_user.id)
    if prompt_id is not None:
        statement = statement.where(PromptTestRun.prompt_id == prompt_id)
    if suite_id is not None:
        statement = statement.where(PromptTestRun.suite_id == suite_id)

    count_statement = select(func.count()).select_from(statement.subquery())
    total = db.exec(count_statement).one()
    runs = db.exec(
        statement.order_by(PromptTestRun.created_at.desc()).offset(skip).limit(limit)
    ).all()

    return success_response(data={
        "items": [dump_model(run) for run in runs],
        "total": total,
        "skip": skip,
        "limit": limit,
    })
