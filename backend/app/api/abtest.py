import time
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.prompt import Prompt
from ..models.abtest import ABTestResult, ABTestCreate, ABTestResponse, PromptExecutionResult
from ..models.quality_evaluation import QualityEvaluation, ComparisonReport
from ..services.openai_service import OpenAIService
from ..services.evaluation_service import EvaluationService
from ..services.rate_limit import rate_limiter
from ..utils.response import success_response, error_response
from .run import replace_variables

router = APIRouter(prefix="/api/abtest", tags=["A/B测试"])


@router.post("", response_model=dict)
async def create_abtest(
    test_data: ABTestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """创建并执行 A/B 测试"""
    
    # 检查频率限制
    allowed, error_msg = rate_limiter.check_rate_limit(current_user.id)
    if not allowed:
        return error_response(code=3001, message=error_msg)
    
    # 验证 Prompt 数量
    if len(test_data.prompt_ids) < 2:
        return error_response(code=4001, message="至少需要2个 Prompt 进行对比")
    
    if len(test_data.prompt_ids) > 5:
        return error_response(code=4002, message="最多支持5个 Prompt 对比")
    
    # 加载所有 Prompts
    prompts = []
    for prompt_id in test_data.prompt_ids:
        prompt = db.get(Prompt, prompt_id)
        if not prompt:
            return error_response(code=2001, message=f"Prompt {prompt_id} 不存在")
        
        # 权限检查
        if prompt.user_id != current_user.id and not prompt.is_public:
            return error_response(code=2002, message=f"无权访问 Prompt {prompt_id}")
        
        prompts.append(prompt)
    
    # 执行测试 - 优化：合并为一次调用
    results = []
    
    # 构建合并的prompt - 使用严格的格式控制
    merged_prompt_parts = []
    
    # 系统角色和任务说明
    merged_prompt_parts.append("# 任务说明\n")
    merged_prompt_parts.append("你是一个专业的文案生成助手。我将提供多个不同风格的Prompt要求，你需要严格按照每个Prompt的要求，生成对应的文案内容。\n\n")
    
    # 格式要求 - 极其重要
    merged_prompt_parts.append("# 输出格式要求（必须严格遵守）\n")
    merged_prompt_parts.append("1. 必须使用指定的分隔符标记每个版本\n")
    merged_prompt_parts.append("2. 分隔符格式：===VERSION_N===（N为版本号，从1开始）\n")
    merged_prompt_parts.append("3. 每个版本的内容只包含文案本身，不要添加任何说明、标题或其他文字\n")
    merged_prompt_parts.append("4. 版本之间用空行分隔\n")
    merged_prompt_parts.append("5. 不要输出任何额外的解释、总结或评论\n\n")
    
    # 输出示例
    merged_prompt_parts.append("# 输出示例\n")
    merged_prompt_parts.append("===VERSION_1===\n")
    merged_prompt_parts.append("[第一个版本的文案内容]\n\n")
    merged_prompt_parts.append("===VERSION_2===\n")
    merged_prompt_parts.append("[第二个版本的文案内容]\n\n")
    merged_prompt_parts.append("===VERSION_3===\n")
    merged_prompt_parts.append("[第三个版本的文案内容]\n\n")
    
    # 各个版本的具体要求
    merged_prompt_parts.append("# 各版本具体要求\n")
    merged_prompt_parts.append(f"请生成 {len(prompts)} 个版本的文案，要求如下：\n\n")
    
    for idx, prompt in enumerate(prompts, 1):
        final_content = replace_variables(prompt.content, test_data.input_variables or {})
        merged_prompt_parts.append(f"## 版本{idx}：{prompt.title}\n")
        merged_prompt_parts.append(f"{final_content}\n\n")
    
    # 再次强调格式
    merged_prompt_parts.append("# 最终输出\n")
    merged_prompt_parts.append("请现在开始生成，直接输出内容，格式如下：\n")
    merged_prompt_parts.append("===VERSION_1===\n")
    merged_prompt_parts.append("[版本1的文案]\n\n")
    merged_prompt_parts.append("===VERSION_2===\n")
    merged_prompt_parts.append("[版本2的文案]\n\n")
    for idx in range(3, len(prompts) + 1):
        merged_prompt_parts.append(f"===VERSION_{idx}===\n")
        merged_prompt_parts.append(f"[版本{idx}的文案]\n\n")
    
    merged_prompt_parts.append("\n【重要】请严格按照上述格式输出，不要添加任何其他内容！")
    
    merged_prompt = "".join(merged_prompt_parts)
    
    # 记录开始时间
    start_time = time.time()
    print(f"开始调用模型(合并模式): {test_data.model}, 测试 {len(prompts)} 个版本")
    
    try:
        # 一次性调用AI
        result = await OpenAIService.chat_completion(
            prompt=merged_prompt,
            model=test_data.model,
            db=db,
            user_id=current_user.id
        )
        
        # 计算总响应时间
        total_response_time = time.time() - start_time
        
        # 解析AI返回的内容，分离各个版本
        output_content = result["output"]
        version_outputs = []
        
        print(f"AI返回的原始内容长度: {len(output_content)}")
        print(f"AI返回内容预览: {output_content[:500]}...")
        
        # 尝试按照===VERSION_N===分割
        import re
        version_pattern = r'===VERSION_(\d+)===\s*\n(.*?)(?====VERSION_\d+===|\Z)'
        matches = re.findall(version_pattern, output_content, re.DOTALL | re.MULTILINE)
        
        print(f"正则匹配到 {len(matches)} 个版本")
        
        if matches and len(matches) >= len(prompts):
            # 成功分离出各个版本
            print("✅ 成功按格式分离各个版本")
            for idx, match in enumerate(matches[:len(prompts)], 1):
                content = match[1].strip()
                # 移除可能的markdown代码块标记
                content = re.sub(r'^```.*\n', '', content)
                content = re.sub(r'\n```$', '', content)
                version_outputs.append(content)
                print(f"版本{idx}内容长度: {len(content)}")
        else:
            # 如果格式不符合预期，尝试其他方式
            print(f"⚠️ 格式不符合预期，尝试备用解析方案")
            
            # 方案2：尝试按VERSION_N分割（不要求===）
            alt_pattern = r'VERSION[_\s]*(\d+)[:\s]*\n(.*?)(?=VERSION[_\s]*\d+|\Z)'
            alt_matches = re.findall(alt_pattern, output_content, re.DOTALL | re.IGNORECASE)
            
            if alt_matches and len(alt_matches) >= len(prompts):
                print("✅ 使用备用方案1成功")
                for match in alt_matches[:len(prompts)]:
                    version_outputs.append(match[1].strip())
            else:
                # 方案3：按段落分割
                print("⚠️ 使用备用方案2：段落分割")
                # 先尝试按两个换行符分割
                parts = output_content.split('\n\n')
                clean_parts = []
                for p in parts:
                    p = p.strip()
                    # 过滤掉标题、分隔符等
                    if p and len(p) > 30 and not p.startswith('#') and not p.startswith('==='):
                        # 移除可能的版本标记
                        p = re.sub(r'^VERSION[_\s]*\d+[:\s]*\n*', '', p, flags=re.IGNORECASE)
                        clean_parts.append(p)
                
                version_outputs = clean_parts[:len(prompts)]
                print(f"段落分割得到 {len(version_outputs)} 个版本")
        
        # 确保有足够的输出
        if len(version_outputs) < len(prompts):
            print(f"⚠️ 版本数量不足，需要{len(prompts)}个，实际{len(version_outputs)}个")
            # 如果完全没有分离成功，就把整个内容分配给第一个版本
            if len(version_outputs) == 0:
                version_outputs.append(output_content)
            # 其他版本使用第一个版本的内容（总比没有好）
            while len(version_outputs) < len(prompts):
                version_outputs.append(version_outputs[0])
        
        # 最终检查：确保每个版本都有内容
        for idx, content in enumerate(version_outputs):
            if not content or len(content) < 10:
                print(f"⚠️ 版本{idx+1}内容为空或过短，使用完整内容")
                version_outputs[idx] = output_content
        
        # 为每个版本分配token和成本（按输出长度比例）
        total_output_tokens = result["output_tokens"]
        total_cost = result["cost"]
        
        output_lengths = [len(output) for output in version_outputs]
        total_length = sum(output_lengths)
        
        # 构造每个版本的结果
        for idx, prompt in enumerate(prompts):
            # 计算该版本的token和成本比例
            if total_length > 0:
                ratio = output_lengths[idx] / total_length
            else:
                ratio = 1.0 / len(prompts)
            
            execution_result = {
                "prompt_id": prompt.id,
                "prompt_title": prompt.title,
                "output": version_outputs[idx],
                "input_tokens": result["input_tokens"] // len(prompts),  # 平均分配
                "output_tokens": int(total_output_tokens * ratio),
                "total_tokens": result["input_tokens"] // len(prompts) + int(total_output_tokens * ratio),
                "response_time": round(total_response_time, 3),  # 所有版本使用相同的总时间
                "model": result["model"],
                "cost": round(total_cost * ratio, 6),  # 按比例分配成本
                "success": True,
                "error": None
            }
            results.append(execution_result)
            
        print(f"成功生成 {len(results)} 个版本的内容")
        
        # AI评测（如果启用）
        if test_data.enable_evaluation:
            print("开始AI质量评测...")
            quality_scores_list = []
            
            for idx, (prompt, result_item) in enumerate(zip(prompts, results)):
                try:
                    evaluation_result = await EvaluationService.evaluate_output_quality(
                        output_content=result_item["output"],
                        prompt_content=prompt.content,
                        db=db,
                        user_id=current_user.id
                    )
                    
                    # 添加评分到结果
                    result_item["quality_score"] = evaluation_result.get("overall_score", 0)
                    result_item["evaluation_details"] = evaluation_result
                    
                    # 保存评测记录
                    quality_eval = QualityEvaluation(
                        user_id=current_user.id,
                        test_type="abtest",
                        test_id=None,  # 稍后更新
                        prompt_id=prompt.id,
                        prompt_content=result_item.get("output", ""),
                        output_content=result_item.get("output", ""),
                        accuracy_score=evaluation_result.get("accuracy_score", 0),
                        relevance_score=evaluation_result.get("relevance_score", 0),
                        fluency_score=evaluation_result.get("fluency_score", 0),
                        creativity_score=evaluation_result.get("creativity_score", 0),
                        safety_score=evaluation_result.get("safety_score", 0),
                        overall_score=evaluation_result.get("overall_score", 0),
                        evaluation_details=evaluation_result.get("evaluation_details", {}),
                        safety_issues=evaluation_result.get("safety_issues", []),
                        has_sensitive_content=evaluation_result.get("has_sensitive_content", False),
                        response_time=result_item.get("response_time", 0),
                        token_count=result_item.get("total_tokens", 0),
                        cost=result_item.get("cost", 0),
                        cost_efficiency_score=EvaluationService.calculate_cost_efficiency(
                            evaluation_result.get("overall_score", 0),
                            result_item.get("cost", 0),
                            result_item.get("response_time", 0)
                        ),
                        strengths=evaluation_result.get("strengths", []),
                        weaknesses=evaluation_result.get("weaknesses", []),
                        suggestions=evaluation_result.get("suggestions", []),
                        evaluation_model=test_data.model
                    )
                    db.add(quality_eval)
                    quality_scores_list.append(evaluation_result)
                    
                except Exception as eval_error:
                    print(f"评测版本{idx+1}失败: {str(eval_error)}")
                    result_item["quality_score"] = 0
                    result_item["evaluation_details"] = {}
            
            # 更新测试结果
            results = results  # Already updated in place
        
    except Exception as e:
        print(f"合并调用失败: {str(e)}")
        # 如果合并调用失败，记录所有版本的失败
        for prompt in prompts:
            execution_result = {
                "prompt_id": prompt.id,
                "prompt_title": prompt.title,
                "output": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "response_time": 0,
                "model": test_data.model,
                "cost": 0,
                "success": False,
                "error": str(e)
            }
            results.append(execution_result)
    
    # 保存测试结果
    abtest = ABTestResult(
        user_id=current_user.id,
        test_name=test_data.test_name,
        input_variables=test_data.input_variables,
        prompt_ids=test_data.prompt_ids,
        results=results
    )
    
    db.add(abtest)
    db.commit()
    db.refresh(abtest)
    
    # 记录请求（合并模式只算一次请求）
    rate_limiter.record_request(current_user.id)
    
    # 生成对比报告（如果启用）
    comparison_report_id = None
    if test_data.generate_report and len(results) > 0:
        try:
            print("生成对比分析报告...")
            prompt_titles = [p.title for p in prompts]
            
            report_data = await EvaluationService.generate_comparison_report(
                abtest_results=results,
                prompt_titles=prompt_titles,
                db=db,
                user_id=current_user.id
            )
            
            # 保存报告
            comparison_report = ComparisonReport(
                user_id=current_user.id,
                abtest_id=abtest.id,
                winner_prompt_id=report_data.get("winner_prompt_id"),
                winner_reason=report_data.get("winner_reason", ""),
                comparison_data=report_data.get("comparison_data", {}),
                chart_data=report_data.get("chart_data", {}),
                summary=report_data.get("summary", ""),
                recommendations=report_data.get("recommendations", [])
            )
            db.add(comparison_report)
            db.commit()
            db.refresh(comparison_report)
            
            comparison_report_id = comparison_report.id
            print(f"对比报告已生成 (ID: {comparison_report_id})")
            
        except Exception as report_error:
            print(f"生成对比报告失败: {str(report_error)}")
    
    # 构造响应
    response = ABTestResponse(
        id=abtest.id,
        user_id=abtest.user_id,
        test_name=abtest.test_name,
        input_variables=abtest.input_variables,
        prompt_ids=abtest.prompt_ids,
        results=abtest.results,
        quality_scores=abtest.quality_scores,
        created_at=abtest.created_at
    )
    
    return success_response(data=response.model_dump(), message="A/B 测试完成")


@router.get("/list", response_model=dict)
async def get_abtest_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取 A/B 测试列表"""
    
    # 构建查询
    statement = select(ABTestResult).where(
        ABTestResult.user_id == current_user.id
    ).order_by(ABTestResult.created_at.desc())
    
    # 总数
    total_count = len(db.exec(statement).all())
    
    # 分页
    statement = statement.offset(skip).limit(limit)
    tests = db.exec(statement).all()
    
    # 转换为响应格式
    items = []
    for test in tests:
        response = ABTestResponse(
            id=test.id,
            user_id=test.user_id,
            test_name=test.test_name,
            input_variables=test.input_variables,
            prompt_ids=test.prompt_ids,
            results=test.results,
            quality_scores=test.quality_scores,
            created_at=test.created_at
        )
        items.append(response.model_dump())
    
    return success_response(data={
        "items": items,
        "total": total_count,
        "skip": skip,
        "limit": limit
    })


@router.get("/{test_id}", response_model=dict)
async def get_abtest_detail(
    test_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取 A/B 测试详情"""
    
    test = db.get(ABTestResult, test_id)
    
    if not test:
        return error_response(code=4003, message="测试记录不存在")
    
    # 权限检查
    if test.user_id != current_user.id:
        return error_response(code=4004, message="无权访问该测试记录")
    
    response = ABTestResponse(
        id=test.id,
        user_id=test.user_id,
        test_name=test.test_name,
        input_variables=test.input_variables,
        prompt_ids=test.prompt_ids,
        results=test.results,
        quality_scores=test.quality_scores,
        created_at=test.created_at
    )
    
    return success_response(data=response.model_dump())


@router.delete("/{test_id}", response_model=dict)
async def delete_abtest(
    test_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """删除 A/B 测试记录"""
    
    test = db.get(ABTestResult, test_id)
    
    if not test:
        return error_response(code=4003, message="测试记录不存在")
    
    # 权限检查
    if test.user_id != current_user.id:
        return error_response(code=4005, message="无权删除该测试记录")
    
    db.delete(test)
    db.commit()
    
    return success_response(message="测试记录删除成功")


@router.get("/{test_id}/report", response_model=dict)
async def get_comparison_report(
    test_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取A/B测试的对比分析报告"""
    
    # 查询报告
    statement = select(ComparisonReport).where(
        ComparisonReport.abtest_id == test_id,
        ComparisonReport.user_id == current_user.id
    )
    report = db.exec(statement).first()
    
    if not report:
        return error_response(code=4006, message="报告不存在")
    
    from ..models.quality_evaluation import ComparisonReportResponse
    
    response = ComparisonReportResponse(
        id=report.id,
        abtest_id=report.abtest_id,
        winner_prompt_id=report.winner_prompt_id,
        winner_reason=report.winner_reason,
        comparison_data=report.comparison_data,
        chart_data=report.chart_data,
        summary=report.summary,
        recommendations=report.recommendations,
        created_at=report.created_at
    )
    
    return success_response(data=response.model_dump())


@router.post("/{test_id}/regenerate-report", response_model=dict)
async def regenerate_comparison_report(
    test_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """重新生成对比分析报告"""
    
    # 获取测试结果
    test = db.get(ABTestResult, test_id)
    
    if not test:
        return error_response(code=4003, message="测试记录不存在")
    
    # 权限检查
    if test.user_id != current_user.id:
        return error_response(code=4004, message="无权访问该测试记录")
    
    # 获取Prompt标题
    prompt_titles = []
    for prompt_id in test.prompt_ids:
        prompt = db.get(Prompt, prompt_id)
        if prompt:
            prompt_titles.append(prompt.title)
        else:
            prompt_titles.append(f"Prompt {prompt_id}")
    
    try:
        # 生成报告
        report_data = await EvaluationService.generate_comparison_report(
            abtest_results=test.results,
            prompt_titles=prompt_titles,
            db=db,
            user_id=current_user.id
        )
        
        # 查找或创建报告记录
        statement = select(ComparisonReport).where(
            ComparisonReport.abtest_id == test_id,
            ComparisonReport.user_id == current_user.id
        )
        report = db.exec(statement).first()
        
        if report:
            # 更新现有报告
            report.winner_prompt_id = report_data.get("winner_prompt_id")
            report.winner_reason = report_data.get("winner_reason", "")
            report.comparison_data = report_data.get("comparison_data", {})
            report.chart_data = report_data.get("chart_data", {})
            report.summary = report_data.get("summary", "")
            report.recommendations = report_data.get("recommendations", [])
        else:
            # 创建新报告
            report = ComparisonReport(
                user_id=current_user.id,
                abtest_id=test_id,
                winner_prompt_id=report_data.get("winner_prompt_id"),
                winner_reason=report_data.get("winner_reason", ""),
                comparison_data=report_data.get("comparison_data", {}),
                chart_data=report_data.get("chart_data", {}),
                summary=report_data.get("summary", ""),
                recommendations=report_data.get("recommendations", [])
            )
            db.add(report)
        
        db.commit()
        db.refresh(report)
        
        from ..models.quality_evaluation import ComparisonReportResponse
        
        response = ComparisonReportResponse(
            id=report.id,
            abtest_id=report.abtest_id,
            winner_prompt_id=report.winner_prompt_id,
            winner_reason=report.winner_reason,
            comparison_data=report.comparison_data,
            chart_data=report.chart_data,
            summary=report.summary,
            recommendations=report.recommendations,
            created_at=report.created_at
        )
        
        return success_response(data=response.model_dump(), message="报告生成成功")
        
    except Exception as e:
        return error_response(code=5001, message=f"生成报告失败: {str(e)}")

