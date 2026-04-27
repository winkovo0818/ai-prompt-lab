import time
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from sqlmodel import Session, select

from ..core.database import engine
from ..models.prompt import Prompt
from ..models.prompt_version import PromptVersion
from ..models.test_suite import PromptTestRun, PromptTestSuite
from ..services.evaluation_service import EvaluationService
from ..services.openai_service import OpenAIService


def replace_variables(content: str, variables: Dict[str, str]) -> str:
    if not variables:
        return content

    result = content
    for key, value in variables.items():
        pattern = r"\{\{\s*" + re.escape(key) + r"(?::[^}]*)?\s*\}\}"
        result = re.sub(pattern, str(value), result)

    return result


class TestRunnerService:
    """Runs reusable prompt test suites against candidate and baseline versions."""

    @staticmethod
    async def run_suite(
        db: Session,
        suite: PromptTestSuite,
        runner_user_id: Optional[int] = None,
        candidate_version: Optional[int] = None,
        baseline_version: Optional[int] = None,
        trigger_source: str = "manual",
        model: Optional[str] = None,
        temperature: float = 0.0,
        enable_evaluation: bool = True,
    ) -> PromptTestRun:
        prompt = db.get(Prompt, suite.prompt_id)
        if not prompt:
            raise ValueError("Prompt 不存在")

        runner_user_id = runner_user_id or suite.user_id
        candidate_version = candidate_version or prompt.version
        baseline_version = baseline_version or TestRunnerService.resolve_baseline_version(
            suite, candidate_version
        )

        run = PromptTestRun(
            suite_id=suite.id,
            user_id=runner_user_id,
            prompt_id=suite.prompt_id,
            candidate_version=candidate_version,
            baseline_version=baseline_version,
            trigger_source=trigger_source,
            status="running",
            summary={},
            results=[],
        )
        db.add(run)
        db.commit()
        db.refresh(run)

        try:
            candidate_content = TestRunnerService.get_prompt_content_for_version(
                db, prompt, candidate_version
            )
            baseline_content = None
            if baseline_version:
                baseline_content = TestRunnerService.get_prompt_content_for_version(
                    db, prompt, baseline_version
                )

            results = []
            for index, test_case in enumerate(suite.test_cases or [], start=1):
                result = await TestRunnerService.run_case(
                    db=db,
                    user_id=runner_user_id,
                    prompt_id=suite.prompt_id,
                    case_index=index,
                    test_case=test_case,
                    candidate_content=candidate_content,
                    baseline_content=baseline_content,
                    model=model or "gpt-3.5-turbo",
                    temperature=temperature,
                    enable_evaluation=enable_evaluation,
                )
                results.append(result)

            summary = TestRunnerService.build_summary(results)
            run.status = "completed"
            run.results = results
            run.summary = summary
            run.completed_at = datetime.utcnow()
        except Exception as exc:
            run.status = "failed"
            run.error = str(exc)
            run.completed_at = datetime.utcnow()

        db.add(run)
        db.commit()
        db.refresh(run)
        return run

    @staticmethod
    def resolve_baseline_version(
        suite: PromptTestSuite, candidate_version: int
    ) -> Optional[int]:
        if suite.baseline_mode == "fixed_version":
            return suite.fixed_baseline_version
        previous_version = candidate_version - 1
        return previous_version if previous_version >= 1 else None

    @staticmethod
    def get_prompt_content_for_version(db: Session, prompt: Prompt, version: int) -> str:
        if prompt.version == version:
            return prompt.content

        prompt_version = db.exec(
            select(PromptVersion).where(
                PromptVersion.prompt_id == prompt.id,
                PromptVersion.version == version,
            )
        ).first()

        if not prompt_version:
            raise ValueError(f"Prompt 版本不存在: v{version}")

        return prompt_version.content

    @staticmethod
    async def run_case(
        db: Session,
        user_id: int,
        prompt_id: int,
        case_index: int,
        test_case: Dict,
        candidate_content: str,
        baseline_content: Optional[str],
        model: str,
        temperature: float,
        enable_evaluation: bool,
    ) -> Dict:
        variables = test_case.get("variables") or {}
        candidate_output, candidate_time, candidate_tokens, candidate_cost = await TestRunnerService.execute_prompt_content(
            db=db,
            user_id=user_id,
            prompt_content=candidate_content,
            variables=variables,
            model=model,
            temperature=temperature,
        )

        baseline_output = None
        baseline_score = None
        if baseline_content:
            baseline_output, _, _, _ = await TestRunnerService.execute_prompt_content(
                db=db,
                user_id=user_id,
                prompt_content=baseline_content,
                variables=variables,
                model=model,
                temperature=temperature,
            )

        candidate_score = None
        if enable_evaluation or test_case.get("min_quality_score") is not None:
            candidate_score = await TestRunnerService.evaluate_output(
                db=db,
                user_id=user_id,
                output=candidate_output,
                prompt_content=replace_variables(candidate_content, variables),
            )
            if baseline_output:
                baseline_score = await TestRunnerService.evaluate_output(
                    db=db,
                    user_id=user_id,
                    output=baseline_output,
                    prompt_content=replace_variables(baseline_content or "", variables),
                )

        assertion_results, passed = TestRunnerService.evaluate_assertions(
            test_case=test_case,
            output=candidate_output,
            quality_score=candidate_score,
            response_time=candidate_time,
        )

        regression = False
        if baseline_score is not None and candidate_score is not None:
            regression = candidate_score + 0.5 < baseline_score

        return {
            "case_index": case_index,
            "name": test_case.get("name") or f"Case {case_index}",
            "variables": variables,
            "passed": passed,
            "regression": regression,
            "assertion_results": assertion_results,
            "candidate_output": candidate_output,
            "baseline_output": baseline_output,
            "candidate_score": candidate_score,
            "baseline_score": baseline_score,
            "response_time": round(candidate_time, 3),
            "total_tokens": candidate_tokens,
            "cost": candidate_cost,
            "error": None,
        }

    @staticmethod
    async def execute_prompt_content(
        db: Session,
        user_id: int,
        prompt_content: str,
        variables: Dict,
        model: str,
        temperature: float,
    ) -> Tuple[str, float, int, float]:
        final_prompt = replace_variables(prompt_content, variables)
        start_time = time.time()
        result = await OpenAIService.chat_completion(
            prompt=final_prompt,
            model=model,
            temperature=temperature,
            max_tokens=2000,
            db=db,
            user_id=user_id,
        )
        return (
            result.get("output", ""),
            time.time() - start_time,
            result.get("total_tokens", 0),
            result.get("cost", 0),
        )

    @staticmethod
    async def evaluate_output(
        db: Session, user_id: int, output: str, prompt_content: str
    ) -> float:
        evaluation = await EvaluationService.evaluate_output_quality(
            output_content=output,
            prompt_content=prompt_content,
            db=db,
            user_id=user_id,
        )
        return evaluation.get("overall_score", 0)

    @staticmethod
    def evaluate_assertions(
        test_case: Dict,
        output: str,
        quality_score: Optional[float],
        response_time: float,
    ) -> Tuple[List[Dict], bool]:
        assertions = []

        for keyword in test_case.get("required_keywords") or []:
            assertions.append({
                "type": "required_keyword",
                "expected": keyword,
                "passed": keyword in output,
            })

        for keyword in test_case.get("forbidden_keywords") or []:
            assertions.append({
                "type": "forbidden_keyword",
                "expected": keyword,
                "passed": keyword not in output,
            })

        expected_output = test_case.get("expected_output")
        if expected_output:
            assertions.append({
                "type": "expected_output_contains",
                "expected": expected_output,
                "passed": expected_output in output,
            })

        min_quality_score = test_case.get("min_quality_score")
        if min_quality_score is not None:
            assertions.append({
                "type": "min_quality_score",
                "expected": min_quality_score,
                "actual": quality_score,
                "passed": quality_score is not None and quality_score >= min_quality_score,
            })

        max_response_time = test_case.get("max_response_time")
        if max_response_time is not None:
            assertions.append({
                "type": "max_response_time",
                "expected": max_response_time,
                "actual": round(response_time, 3),
                "passed": response_time <= max_response_time,
            })

        passed = all(item["passed"] for item in assertions) if assertions else True
        return assertions, passed

    @staticmethod
    def build_summary(results: List[Dict]) -> Dict:
        total_cases = len(results)
        passed_cases = sum(1 for item in results if item.get("passed"))
        failed_cases = total_cases - passed_cases
        score_values = [item["candidate_score"] for item in results if item.get("candidate_score") is not None]
        response_times = [item.get("response_time", 0) for item in results]
        regression_cases = sum(1 for item in results if item.get("regression"))

        return {
            "total_cases": total_cases,
            "passed_cases": passed_cases,
            "failed_cases": failed_cases,
            "pass_rate": round(passed_cases / total_cases * 100, 2) if total_cases else 0,
            "avg_quality_score": round(sum(score_values) / len(score_values), 2) if score_values else 0,
            "avg_response_time": round(sum(response_times) / len(response_times), 3) if response_times else 0,
            "regression_cases": regression_cases,
            "passed_gate": total_cases > 0 and (passed_cases / total_cases) >= 0.9 and regression_cases == 0,
        }

    @staticmethod
    async def run_auto_smoke_suites(prompt_id: int, candidate_version: int, user_id: int) -> None:
        with Session(engine) as db:
            suites = db.exec(
                select(PromptTestSuite).where(
                    PromptTestSuite.prompt_id == prompt_id,
                    PromptTestSuite.user_id == user_id,
                    PromptTestSuite.suite_type == "smoke",
                    PromptTestSuite.is_active == True,
                    PromptTestSuite.auto_run_on_save == True,
                )
            ).all()

            for suite in suites:
                await TestRunnerService.run_suite(
                    db=db,
                    suite=suite,
                    runner_user_id=user_id,
                    candidate_version=candidate_version,
                    trigger_source="save",
                    temperature=0.0,
                    enable_evaluation=True,
                )
