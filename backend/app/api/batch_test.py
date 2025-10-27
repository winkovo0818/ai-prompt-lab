"""批量测试API - 支持多组输入数据的自动化测试"""
import time
from typing import List, Dict
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from datetime import datetime

from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.prompt import Prompt
from ..models.quality_evaluation import (
    BatchTestResult, BatchTestRequest, BatchTestResponse,
    QualityEvaluation
)
from ..services.openai_service import OpenAIService
from ..services.evaluation_service import EvaluationService
from ..services.rate_limit import rate_limiter
from ..utils.response import success_response, error_response
from .run import replace_variables

router = APIRouter(prefix="/api/batch-test", tags=["批量测试"])


@router.post("", response_model=dict)
async def create_batch_test(
    test_data: BatchTestRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """创建并执行批量测试"""
    
    # 检查频率限制
    allowed, error_msg = rate_limiter.check_rate_limit(current_user.id)
    if not allowed:
        return error_response(code=3001, message=error_msg)
    
    # 验证测试用例数量
    if len(test_data.test_cases) == 0:
        return error_response(code=4001, message="至少需要1个测试用例")
    
    if len(test_data.test_cases) > 50:
        return error_response(code=4002, message="最多支持50个测试用例")
    
    # 加载Prompt
    prompt = db.get(Prompt, test_data.prompt_id)
    if not prompt:
        return error_response(code=2001, message="Prompt 不存在")
    
    # 权限检查
    if prompt.user_id != current_user.id and not prompt.is_public:
        return error_response(code=2002, message="无权访问该 Prompt")
    
    # 创建批量测试记录
    batch_test = BatchTestResult(
        user_id=current_user.id,
        test_name=test_data.test_name,
        prompt_id=test_data.prompt_id,
        test_cases=test_data.test_cases,
        results=[],
        total_cases=len(test_data.test_cases),
        success_count=0,
        failure_count=0,
        model=test_data.model,
        temperature=test_data.temperature
    )
    
    db.add(batch_test)
    db.commit()
    db.refresh(batch_test)
    
    # 执行每个测试用例
    results = []
    total_response_time = 0
    total_token_count = 0
    total_cost = 0
    total_quality_score = 0
    success_count = 0
    failure_count = 0
    
    print(f"开始执行批量测试: {test_data.test_name}, 共 {len(test_data.test_cases)} 个用例")
    
    for idx, test_case in enumerate(test_data.test_cases, 1):
        print(f"执行测试用例 {idx}/{len(test_data.test_cases)}...")
        
        try:
            # 替换变量
            variables = test_case.get("variables", {})
            final_prompt = replace_variables(prompt.content, variables)
            
            # 执行AI调用
            start_time = time.time()
            ai_result = await OpenAIService.chat_completion(
                prompt=final_prompt,
                model=test_data.model,
                temperature=test_data.temperature,
                max_tokens=2000,
                db=db,
                user_id=current_user.id
            )
            response_time = time.time() - start_time
            
            # 评测输出质量（如果启用）
            quality_score = 0
            evaluation_data = {}
            
            if test_data.enable_evaluation:
                try:
                    evaluation_result = await EvaluationService.evaluate_output_quality(
                        output_content=ai_result["output"],
                        prompt_content=final_prompt,
                        db=db,
                        user_id=current_user.id
                    )
                    quality_score = evaluation_result.get("overall_score", 0)
                    evaluation_data = evaluation_result
                    
                    # 保存评测记录
                    quality_eval = QualityEvaluation(
                        user_id=current_user.id,
                        test_type="batch",
                        test_id=batch_test.id,
                        prompt_id=test_data.prompt_id,
                        prompt_content=final_prompt,
                        output_content=ai_result["output"],
                        accuracy_score=evaluation_result.get("accuracy_score", 0),
                        relevance_score=evaluation_result.get("relevance_score", 0),
                        fluency_score=evaluation_result.get("fluency_score", 0),
                        creativity_score=evaluation_result.get("creativity_score", 0),
                        safety_score=evaluation_result.get("safety_score", 0),
                        overall_score=quality_score,
                        evaluation_details=evaluation_result.get("evaluation_details", {}),
                        safety_issues=evaluation_result.get("safety_issues", []),
                        has_sensitive_content=evaluation_result.get("has_sensitive_content", False),
                        response_time=response_time,
                        token_count=ai_result["total_tokens"],
                        cost=ai_result["cost"],
                        cost_efficiency_score=EvaluationService.calculate_cost_efficiency(
                            quality_score, ai_result["cost"], response_time
                        ),
                        strengths=evaluation_result.get("strengths", []),
                        weaknesses=evaluation_result.get("weaknesses", []),
                        suggestions=evaluation_result.get("suggestions", []),
                        evaluation_model=test_data.model
                    )
                    db.add(quality_eval)
                    
                except Exception as eval_error:
                    print(f"评测失败: {str(eval_error)}")
                    quality_score = 0
            
            # 记录结果
            test_result = {
                "test_case_index": idx,
                "variables": variables,
                "expected_output": test_case.get("expected_output"),
                "actual_output": ai_result["output"],
                "input_tokens": ai_result["input_tokens"],
                "output_tokens": ai_result["output_tokens"],
                "total_tokens": ai_result["total_tokens"],
                "response_time": round(response_time, 3),
                "cost": ai_result["cost"],
                "quality_score": quality_score,
                "evaluation_data": evaluation_data,
                "success": True,
                "error": None
            }
            
            results.append(test_result)
            success_count += 1
            
            # 累计统计
            total_response_time += response_time
            total_token_count += ai_result["total_tokens"]
            total_cost += ai_result["cost"]
            total_quality_score += quality_score
            
            # 记录请求
            rate_limiter.record_request(current_user.id)
            
        except Exception as e:
            print(f"测试用例 {idx} 执行失败: {str(e)}")
            
            test_result = {
                "test_case_index": idx,
                "variables": test_case.get("variables", {}),
                "expected_output": test_case.get("expected_output"),
                "actual_output": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "response_time": 0,
                "cost": 0,
                "quality_score": 0,
                "evaluation_data": {},
                "success": False,
                "error": str(e)
            }
            
            results.append(test_result)
            failure_count += 1
    
    # 计算平均值
    test_count = len(test_data.test_cases)
    avg_response_time = total_response_time / test_count if test_count > 0 else 0
    avg_token_count = total_token_count // test_count if test_count > 0 else 0
    avg_cost = total_cost / test_count if test_count > 0 else 0
    avg_quality_score = total_quality_score / success_count if success_count > 0 else 0
    
    # 更新批量测试记录
    batch_test.results = results
    batch_test.success_count = success_count
    batch_test.failure_count = failure_count
    batch_test.avg_response_time = round(avg_response_time, 3)
    batch_test.avg_token_count = avg_token_count
    batch_test.avg_cost = round(avg_cost, 6)
    batch_test.avg_quality_score = round(avg_quality_score, 2)
    batch_test.completed_at = datetime.utcnow()
    
    db.add(batch_test)
    db.commit()
    db.refresh(batch_test)
    
    print(f"批量测试完成: 成功 {success_count}/{test_count}")
    
    # 构造响应
    response = BatchTestResponse(
        id=batch_test.id,
        test_name=batch_test.test_name,
        prompt_id=batch_test.prompt_id,
        total_cases=batch_test.total_cases,
        success_count=batch_test.success_count,
        failure_count=batch_test.failure_count,
        avg_response_time=batch_test.avg_response_time,
        avg_token_count=batch_test.avg_token_count,
        avg_cost=batch_test.avg_cost,
        avg_quality_score=batch_test.avg_quality_score,
        results=batch_test.results,
        created_at=batch_test.created_at,
        completed_at=batch_test.completed_at
    )
    
    return success_response(data=response.model_dump(), message="批量测试完成")


@router.get("/list", response_model=dict)
async def get_batch_test_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取批量测试列表"""
    
    statement = select(BatchTestResult).where(
        BatchTestResult.user_id == current_user.id
    ).order_by(BatchTestResult.created_at.desc())
    
    # 总数
    total_count = len(db.exec(statement).all())
    
    # 分页
    statement = statement.offset(skip).limit(limit)
    tests = db.exec(statement).all()
    
    # 转换为响应格式
    items = []
    for test in tests:
        response = BatchTestResponse(
            id=test.id,
            test_name=test.test_name,
            prompt_id=test.prompt_id,
            total_cases=test.total_cases,
            success_count=test.success_count,
            failure_count=test.failure_count,
            avg_response_time=test.avg_response_time,
            avg_token_count=test.avg_token_count,
            avg_cost=test.avg_cost,
            avg_quality_score=test.avg_quality_score,
            results=test.results,
            created_at=test.created_at,
            completed_at=test.completed_at
        )
        items.append(response.model_dump())
    
    return success_response(data={
        "items": items,
        "total": total_count,
        "skip": skip,
        "limit": limit
    })


@router.get("/{test_id}", response_model=dict)
async def get_batch_test_detail(
    test_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取批量测试详情"""
    
    test = db.get(BatchTestResult, test_id)
    
    if not test:
        return error_response(code=4003, message="测试记录不存在")
    
    # 权限检查
    if test.user_id != current_user.id:
        return error_response(code=4004, message="无权访问该测试记录")
    
    response = BatchTestResponse(
        id=test.id,
        test_name=test.test_name,
        prompt_id=test.prompt_id,
        total_cases=test.total_cases,
        success_count=test.success_count,
        failure_count=test.failure_count,
        avg_response_time=test.avg_response_time,
        avg_token_count=test.avg_token_count,
        avg_cost=test.avg_cost,
        avg_quality_score=test.avg_quality_score,
        results=test.results,
        created_at=test.created_at,
        completed_at=test.completed_at
    )
    
    return success_response(data=response.model_dump())


@router.delete("/{test_id}", response_model=dict)
async def delete_batch_test(
    test_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """删除批量测试记录"""
    
    test = db.get(BatchTestResult, test_id)
    
    if not test:
        return error_response(code=4003, message="测试记录不存在")
    
    # 权限检查
    if test.user_id != current_user.id:
        return error_response(code=4005, message="无权删除该测试记录")
    
    # 删除相关的评测记录
    eval_statement = select(QualityEvaluation).where(
        QualityEvaluation.test_type == "batch",
        QualityEvaluation.test_id == test_id
    )
    evaluations = db.exec(eval_statement).all()
    for evaluation in evaluations:
        db.delete(evaluation)
    
    db.delete(test)
    db.commit()
    
    return success_response(message="测试记录删除成功")


@router.post("/{test_id}/export", response_model=dict)
async def export_batch_test_results(
    test_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """导出批量测试结果（生成报告）"""
    
    test = db.get(BatchTestResult, test_id)
    
    if not test:
        return error_response(code=4003, message="测试记录不存在")
    
    # 权限检查
    if test.user_id != current_user.id:
        return error_response(code=4004, message="无权访问该测试记录")
    
    # 生成报告数据
    report_data = {
        "test_name": test.test_name,
        "test_id": test.id,
        "created_at": test.created_at.isoformat(),
        "completed_at": test.completed_at.isoformat() if test.completed_at else None,
        "summary": {
            "total_cases": test.total_cases,
            "success_count": test.success_count,
            "failure_count": test.failure_count,
            "success_rate": f"{(test.success_count / test.total_cases * 100):.1f}%" if test.total_cases > 0 else "0%",
            "avg_response_time": f"{test.avg_response_time:.3f}s",
            "avg_token_count": test.avg_token_count,
            "avg_cost": f"${test.avg_cost:.6f}",
            "avg_quality_score": f"{test.avg_quality_score:.2f}/10"
        },
        "results": test.results
    }
    
    return success_response(data=report_data, message="报告生成成功")

