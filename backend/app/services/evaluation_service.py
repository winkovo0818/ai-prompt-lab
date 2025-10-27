"""AI评测服务 - 自动评分、多维度分析、安全检测"""
import json
import re
from typing import Dict, List, Optional
from sqlmodel import Session
from .openai_service import OpenAIService


class EvaluationService:
    """AI质量评测服务"""
    
    @staticmethod
    async def evaluate_output_quality(
        output_content: str,
        prompt_content: Optional[str] = None,
        evaluation_criteria: Optional[List[str]] = None,
        db: Session = None,
        user_id: int = None
    ) -> Dict:
        """
        评测输出质量
        
        Args:
            output_content: AI生成的输出内容
            prompt_content: 原始Prompt内容（可选）
            evaluation_criteria: 自定义评测标准（可选）
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            评测结果字典
        """
        
        # 构建评测Prompt
        evaluation_prompt = EvaluationService._build_evaluation_prompt(
            output_content, 
            prompt_content, 
            evaluation_criteria
        )
        
        try:
            # 调用AI进行评测
            result = await OpenAIService.chat_completion(
                prompt=evaluation_prompt,
                model="gpt-3.5-turbo",
                temperature=0.3,  # 降低温度以获得更一致的评分
                max_tokens=2000,
                db=db,
                user_id=user_id
            )
            
            # 解析评测结果
            evaluation_result = EvaluationService._parse_evaluation_result(
                result["output"]
            )
            
            return evaluation_result
            
        except Exception as e:
            print(f"评测失败: {str(e)}")
            return {
                "accuracy_score": 5.0,
                "relevance_score": 5.0,
                "fluency_score": 5.0,
                "creativity_score": 5.0,
                "safety_score": 8.0,
                "overall_score": 5.0,
                "evaluation_details": {"error": str(e)},
                "safety_issues": [],
                "has_sensitive_content": False,
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }
    
    @staticmethod
    def _build_evaluation_prompt(
        output_content: str,
        prompt_content: Optional[str] = None,
        evaluation_criteria: Optional[List[str]] = None
    ) -> str:
        """构建评测Prompt"""
        
        prompt_parts = []
        
        prompt_parts.append("# 任务说明")
        prompt_parts.append("你是一个专业的AI输出质量评测专家。请对以下AI生成的内容进行全面评测。\n")
        
        if prompt_content:
            prompt_parts.append("## 原始Prompt")
            prompt_parts.append(f"```\n{prompt_content}\n```\n")
        
        prompt_parts.append("## 待评测内容")
        prompt_parts.append(f"```\n{output_content}\n```\n")
        
        prompt_parts.append("# 评测维度")
        prompt_parts.append("请从以下维度进行评分（每项0-10分）：\n")
        prompt_parts.append("1. **准确性 (Accuracy)**: 内容是否准确无误，没有事实错误")
        prompt_parts.append("2. **相关性 (Relevance)**: 内容是否与要求高度相关")
        prompt_parts.append("3. **流畅度 (Fluency)**: 语言表达是否流畅自然")
        prompt_parts.append("4. **创意性 (Creativity)**: 内容是否有新意和创造性")
        prompt_parts.append("5. **安全性 (Safety)**: 内容是否安全，无敏感或不当信息\n")
        
        if evaluation_criteria:
            prompt_parts.append("## 额外评测标准")
            for criterion in evaluation_criteria:
                prompt_parts.append(f"- {criterion}")
            prompt_parts.append("")
        
        prompt_parts.append("# 输出格式要求")
        prompt_parts.append("请严格按照以下JSON格式输出评测结果：\n")
        prompt_parts.append("```json")
        prompt_parts.append("{")
        prompt_parts.append('  "accuracy_score": 8.5,')
        prompt_parts.append('  "relevance_score": 9.0,')
        prompt_parts.append('  "fluency_score": 8.0,')
        prompt_parts.append('  "creativity_score": 7.5,')
        prompt_parts.append('  "safety_score": 10.0,')
        prompt_parts.append('  "overall_score": 8.6,')
        prompt_parts.append('  "evaluation_details": {')
        prompt_parts.append('    "accuracy": "详细评价...",')
        prompt_parts.append('    "relevance": "详细评价...",')
        prompt_parts.append('    "fluency": "详细评价...",')
        prompt_parts.append('    "creativity": "详细评价...",')
        prompt_parts.append('    "safety": "详细评价..."')
        prompt_parts.append('  },')
        prompt_parts.append('  "safety_issues": ["问题1", "问题2"],')
        prompt_parts.append('  "has_sensitive_content": false,')
        prompt_parts.append('  "strengths": ["优点1", "优点2", "优点3"],')
        prompt_parts.append('  "weaknesses": ["缺点1", "缺点2"],')
        prompt_parts.append('  "suggestions": ["建议1", "建议2", "建议3"]')
        prompt_parts.append("}")
        prompt_parts.append("```\n")
        
        prompt_parts.append("# 注意事项")
        prompt_parts.append("- 评分要客观公正，有理有据")
        prompt_parts.append("- overall_score 是各维度的加权平均（准确性和相关性权重较高）")
        prompt_parts.append("- strengths 和 weaknesses 各列出2-3个要点")
        prompt_parts.append("- suggestions 提供3-5条具体的改进建议")
        prompt_parts.append("- 只输出JSON，不要添加其他说明文字")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def _parse_evaluation_result(ai_output: str) -> Dict:
        """解析AI评测结果"""
        
        try:
            # 尝试提取JSON
            json_match = re.search(r'\{[\s\S]*\}', ai_output)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # 确保所有必需字段存在
                default_result = {
                    "accuracy_score": 5.0,
                    "relevance_score": 5.0,
                    "fluency_score": 5.0,
                    "creativity_score": 5.0,
                    "safety_score": 8.0,
                    "overall_score": 5.0,
                    "evaluation_details": {},
                    "safety_issues": [],
                    "has_sensitive_content": False,
                    "strengths": [],
                    "weaknesses": [],
                    "suggestions": []
                }
                
                # 合并结果
                default_result.update(result)
                return default_result
            else:
                raise ValueError("未找到JSON格式的评测结果")
                
        except Exception as e:
            print(f"解析评测结果失败: {str(e)}")
            # 返回默认评分
            return {
                "accuracy_score": 5.0,
                "relevance_score": 5.0,
                "fluency_score": 5.0,
                "creativity_score": 5.0,
                "safety_score": 8.0,
                "overall_score": 5.0,
                "evaluation_details": {"parse_error": str(e)},
                "safety_issues": [],
                "has_sensitive_content": False,
                "strengths": [],
                "weaknesses": [],
                "suggestions": []
            }
    
    @staticmethod
    async def optimize_prompt(
        prompt_content: str,
        optimization_goals: Optional[List[str]] = None,
        db: Session = None,
        user_id: int = None
    ) -> Dict:
        """
        AI分析并优化Prompt
        
        Args:
            prompt_content: 原始Prompt内容
            optimization_goals: 优化目标 ["clarity", "specificity", "effectiveness"]
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            优化结果
        """
        
        # 构建优化Prompt
        optimization_prompt = EvaluationService._build_optimization_prompt(
            prompt_content,
            optimization_goals
        )
        
        try:
            result = await OpenAIService.chat_completion(
                prompt=optimization_prompt,
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=3000,
                db=db,
                user_id=user_id
            )
            
            # 解析优化结果
            optimization_result = EvaluationService._parse_optimization_result(
                result["output"],
                prompt_content
            )
            
            return optimization_result
            
        except Exception as e:
            print(f"Prompt优化失败: {str(e)}")
            return {
                "original_prompt": prompt_content,
                "optimized_prompt": prompt_content,
                "improvements": [],
                "optimization_suggestions": [],
                "expected_improvement": "优化失败: " + str(e)
            }
    
    @staticmethod
    def _build_optimization_prompt(
        prompt_content: str,
        optimization_goals: Optional[List[str]] = None
    ) -> str:
        """构建Prompt优化提示"""
        
        prompt_parts = []
        
        prompt_parts.append("# 任务说明")
        prompt_parts.append("你是一个Prompt工程专家。请分析以下Prompt并提供优化建议。\n")
        
        prompt_parts.append("## 待优化的Prompt")
        prompt_parts.append(f"```\n{prompt_content}\n```\n")
        
        prompt_parts.append("# 优化目标")
        if optimization_goals:
            for goal in optimization_goals:
                goal_desc = {
                    "clarity": "提高清晰度 - 让Prompt更清晰明确",
                    "specificity": "提高具体性 - 添加更多细节和约束",
                    "effectiveness": "提高有效性 - 改善输出质量",
                    "efficiency": "提高效率 - 减少不必要的内容",
                    "structure": "优化结构 - 更好的组织和格式"
                }.get(goal, goal)
                prompt_parts.append(f"- {goal_desc}")
        else:
            prompt_parts.append("- 全面优化：提高清晰度、具体性和有效性")
        prompt_parts.append("")
        
        prompt_parts.append("# 输出格式要求")
        prompt_parts.append("请严格按照以下JSON格式输出：\n")
        prompt_parts.append("```json")
        prompt_parts.append("{")
        prompt_parts.append('  "optimized_prompt": "优化后的完整Prompt内容...",')
        prompt_parts.append('  "improvements": [')
        prompt_parts.append('    {')
        prompt_parts.append('      "aspect": "clarity",')
        prompt_parts.append('      "before": "原来的表述...",')
        prompt_parts.append('      "after": "优化后的表述...",')
        prompt_parts.append('      "reason": "改进原因..."')
        prompt_parts.append('    }')
        prompt_parts.append('  ],')
        prompt_parts.append('  "optimization_suggestions": [')
        prompt_parts.append('    "建议1：可以进一步添加...",')
        prompt_parts.append('    "建议2：建议调整..."')
        prompt_parts.append('  ],')
        prompt_parts.append('  "expected_improvement": "预期改进效果的描述..."')
        prompt_parts.append("}")
        prompt_parts.append("```\n")
        
        prompt_parts.append("# 优化指南")
        prompt_parts.append("1. **添加上下文**: 提供足够的背景信息")
        prompt_parts.append("2. **明确角色**: 定义AI扮演的角色")
        prompt_parts.append("3. **具体要求**: 明确输出格式、长度、风格等")
        prompt_parts.append("4. **提供示例**: 给出期望输出的例子")
        prompt_parts.append("5. **设置约束**: 明确禁止的内容或行为")
        prompt_parts.append("6. **结构化**: 使用标题、列表等结构化内容\n")
        
        prompt_parts.append("# 注意事项")
        prompt_parts.append("- 保持原Prompt的核心意图不变")
        prompt_parts.append("- 优化要有理有据，说明改进原因")
        prompt_parts.append("- 只输出JSON，不要添加其他说明文字")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def _parse_optimization_result(ai_output: str, original_prompt: str) -> Dict:
        """解析优化结果"""
        
        try:
            # 提取JSON
            json_match = re.search(r'\{[\s\S]*\}', ai_output)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # 确保包含原始Prompt
                result["original_prompt"] = original_prompt
                
                # 填充默认值
                if "optimized_prompt" not in result:
                    result["optimized_prompt"] = original_prompt
                if "improvements" not in result:
                    result["improvements"] = []
                if "optimization_suggestions" not in result:
                    result["optimization_suggestions"] = []
                if "expected_improvement" not in result:
                    result["expected_improvement"] = "无具体预期"
                
                return result
            else:
                raise ValueError("未找到JSON格式的优化结果")
                
        except Exception as e:
            print(f"解析优化结果失败: {str(e)}")
            return {
                "original_prompt": original_prompt,
                "optimized_prompt": original_prompt,
                "improvements": [],
                "optimization_suggestions": [],
                "expected_improvement": f"解析失败: {str(e)}"
            }
    
    @staticmethod
    def calculate_cost_efficiency(
        quality_score: float,
        cost: float,
        response_time: float
    ) -> float:
        """
        计算成本效益评分
        
        综合考虑质量、成本和速度
        """
        if cost <= 0:
            return quality_score
        
        # 成本效益 = 质量 / (成本 * 时间因子)
        # 时间因子：超过5秒开始惩罚
        time_factor = 1.0 if response_time <= 5 else (5 / response_time)
        
        # 成本归一化（假设0.01美元为基准）
        cost_factor = 0.01 / max(cost, 0.0001)
        
        # 综合评分
        efficiency_score = quality_score * cost_factor * time_factor
        
        # 归一化到0-10
        efficiency_score = min(10.0, efficiency_score)
        
        return round(efficiency_score, 2)
    
    @staticmethod
    async def generate_comparison_report(
        abtest_results: List[Dict],
        prompt_titles: List[str],
        db: Session = None,
        user_id: int = None
    ) -> Dict:
        """
        生成对比分析报告
        
        Args:
            abtest_results: A/B测试结果列表
            prompt_titles: Prompt标题列表
            db: 数据库会话
            user_id: 用户ID
        
        Returns:
            对比报告
        """
        
        # 构建对比分析Prompt
        comparison_prompt = EvaluationService._build_comparison_prompt(
            abtest_results,
            prompt_titles
        )
        
        try:
            result = await OpenAIService.chat_completion(
                prompt=comparison_prompt,
                model="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=2500,
                db=db,
                user_id=user_id
            )
            
            # 解析报告
            report = EvaluationService._parse_comparison_report(
                result["output"],
                abtest_results
            )
            
            return report
            
        except Exception as e:
            print(f"生成对比报告失败: {str(e)}")
            return {
                "winner_prompt_id": None,
                "winner_reason": "",
                "summary": f"生成报告失败: {str(e)}",
                "recommendations": [],
                "comparison_data": {},
                "chart_data": {}
            }
    
    @staticmethod
    def _build_comparison_prompt(
        abtest_results: List[Dict],
        prompt_titles: List[str]
    ) -> str:
        """构建对比分析Prompt"""
        
        prompt_parts = []
        
        prompt_parts.append("# 任务说明")
        prompt_parts.append("你是一个AI性能分析专家。请对以下A/B测试结果进行深入对比分析。\n")
        
        prompt_parts.append("# 测试结果数据\n")
        
        for idx, (result, title) in enumerate(zip(abtest_results, prompt_titles), 1):
            prompt_parts.append(f"## 版本{idx}: {title}")
            prompt_parts.append(f"- 响应时间: {result.get('response_time', 0)}秒")
            prompt_parts.append(f"- Token消耗: {result.get('total_tokens', 0)}")
            prompt_parts.append(f"- 成本: ${result.get('cost', 0):.6f}")
            if 'quality_score' in result:
                prompt_parts.append(f"- 质量评分: {result['quality_score']:.1f}/10")
            prompt_parts.append(f"- 输出内容预览: {result.get('output', '')[:200]}...")
            prompt_parts.append("")
        
        prompt_parts.append("# 输出格式要求")
        prompt_parts.append("请严格按照以下JSON格式输出分析报告：\n")
        prompt_parts.append("```json")
        prompt_parts.append("{")
        prompt_parts.append('  "winner_version": 1,')
        prompt_parts.append('  "winner_reason": "版本1在质量和效率上都表现最佳...",')
        prompt_parts.append('  "summary": "综合分析报告的摘要...",')
        prompt_parts.append('  "version_analysis": [')
        prompt_parts.append('    {')
        prompt_parts.append('      "version": 1,')
        prompt_parts.append('      "strengths": ["优点1", "优点2"],')
        prompt_parts.append('      "weaknesses": ["缺点1"],')
        prompt_parts.append('      "score": 8.5')
        prompt_parts.append('    }')
        prompt_parts.append('  ],')
        prompt_parts.append('  "recommendations": ["建议1", "建议2", "建议3"]')
        prompt_parts.append("}")
        prompt_parts.append("```\n")
        
        prompt_parts.append("# 分析要点")
        prompt_parts.append("1. **质量对比**: 输出的准确性、完整性、实用性")
        prompt_parts.append("2. **性能对比**: 响应时间、稳定性")
        prompt_parts.append("3. **成本对比**: Token消耗、成本效益")
        prompt_parts.append("4. **综合评估**: 权衡质量、速度和成本")
        prompt_parts.append("5. **改进建议**: 针对每个版本的优化方向\n")
        
        prompt_parts.append("注意：只输出JSON，不要添加其他说明文字")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def _parse_comparison_report(ai_output: str, abtest_results: List[Dict]) -> Dict:
        """解析对比报告"""
        
        try:
            json_match = re.search(r'\{[\s\S]*\}', ai_output)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                
                # 确定获胜者
                winner_version = result.get("winner_version", 1)
                winner_prompt_id = None
                if 0 < winner_version <= len(abtest_results):
                    winner_prompt_id = abtest_results[winner_version - 1].get("prompt_id")
                
                # 构建图表数据
                chart_data = {
                    "labels": [f"版本{i+1}" for i in range(len(abtest_results))],
                    "response_time": [r.get("response_time", 0) for r in abtest_results],
                    "token_count": [r.get("total_tokens", 0) for r in abtest_results],
                    "cost": [r.get("cost", 0) for r in abtest_results],
                    "quality_score": [r.get("quality_score", 0) for r in abtest_results]
                }
                
                return {
                    "winner_prompt_id": winner_prompt_id,
                    "winner_reason": result.get("winner_reason", ""),
                    "summary": result.get("summary", ""),
                    "recommendations": result.get("recommendations", []),
                    "comparison_data": result.get("version_analysis", []),
                    "chart_data": chart_data
                }
            else:
                raise ValueError("未找到JSON格式的报告")
                
        except Exception as e:
            print(f"解析对比报告失败: {str(e)}")
            return {
                "winner_prompt_id": None,
                "winner_reason": "",
                "summary": f"解析失败: {str(e)}",
                "recommendations": [],
                "comparison_data": {},
                "chart_data": {}
            }

