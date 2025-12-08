"""
Prompt 分析服务
使用 AI 分析 Prompt 质量并给出改进建议
"""
import json
from typing import Dict, Optional
from sqlmodel import Session
from .openai_service import OpenAIService


# 分析用的系统提示词
ANALYZER_SYSTEM_PROMPT = """你是一位专业的 Prompt 工程师，专门分析和优化 AI 提示词。

请分析用户提供的 Prompt，从以下维度进行评估：

1. **清晰度** (0-100分)：目标是否明确，表达是否清晰
2. **结构性** (0-100分)：是否有良好的结构和组织
3. **完整性** (0-100分)：上下文、约束条件是否完整
4. **可执行性** (0-100分)：AI 是否能准确理解并执行

请以 JSON 格式输出分析结果，格式如下：
{
  "overall_score": 85,
  "dimensions": {
    "clarity": {"score": 90, "comment": "目标明确"},
    "structure": {"score": 80, "comment": "结构清晰，但可以更好"},
    "completeness": {"score": 85, "comment": "上下文完整"},
    "executability": {"score": 85, "comment": "指令清晰可执行"}
  },
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["不足1", "不足2"],
  "suggestions": [
    {
      "type": "structure",
      "priority": "high",
      "title": "建议标题",
      "description": "具体建议描述",
      "example": "改进后的示例（如果适用）"
    }
  ],
  "optimized_prompt": "优化后的完整 Prompt（保留原意但改进表达）",
  "best_practices": [
    {
      "rule": "规则名称",
      "status": "pass/fail",
      "message": "说明"
    }
  ]
}

最佳实践检查项：
- 是否使用了角色设定
- 是否有明确的输出格式要求
- 是否提供了示例（Few-shot）
- 是否有适当的约束条件
- 是否避免了歧义表达
- 变量占位符是否正确使用（如 {{variable}}）

请严格输出 JSON 格式，不要包含其他内容。"""


class PromptAnalyzer:
    """Prompt 分析器"""
    
    @staticmethod
    async def analyze(
        prompt_content: str,
        db: Session,
        user_id: int,
        prompt_title: Optional[str] = None
    ) -> Dict:
        """
        分析 Prompt 并返回评估结果
        
        Args:
            prompt_content: Prompt 内容
            db: 数据库会话
            user_id: 用户 ID
            prompt_title: Prompt 标题（可选）
        
        Returns:
            分析结果字典
        """
        # 构建分析请求
        user_message = f"""请分析以下 Prompt：

{"标题：" + prompt_title if prompt_title else ""}

---
{prompt_content}
---

请给出详细的分析报告和改进建议。"""

        try:
            # 调用 AI 服务进行分析
            response = await OpenAIService.chat_completion(
                prompt=user_message,
                model="gpt-4o-mini",  # 使用更智能的模型进行分析
                temperature=0.3,  # 低温度以获得更稳定的输出
                max_tokens=2000,
                db=db,
                user_id=user_id,
                system_prompt=ANALYZER_SYSTEM_PROMPT
            )
            
            # 解析 AI 返回的 JSON
            content = response.get("content", "")
            
            # 尝试提取 JSON
            analysis_result = PromptAnalyzer._parse_json_response(content)
            
            if analysis_result:
                return {
                    "success": True,
                    "analysis": analysis_result,
                    "tokens_used": response.get("total_tokens", 0)
                }
            else:
                return {
                    "success": False,
                    "error": "无法解析分析结果",
                    "raw_response": content
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def _parse_json_response(content: str) -> Optional[Dict]:
        """解析 AI 返回的 JSON 内容"""
        try:
            # 直接尝试解析
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 JSON 块
        import re
        json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        matches = re.findall(json_pattern, content)
        
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        
        # 尝试找到 { 和 } 之间的内容
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(content[start:end])
        except json.JSONDecodeError:
            pass
        
        return None
    
    @staticmethod
    def get_quick_tips(prompt_content: str) -> Dict:
        """
        快速本地分析，不调用 AI
        返回基本的格式检查结果
        """
        tips = []
        score = 100
        
        # 检查长度
        if len(prompt_content) < 20:
            tips.append({
                "type": "warning",
                "message": "Prompt 过短，建议添加更多上下文"
            })
            score -= 15
        
        # 检查变量占位符
        import re
        variables = re.findall(r'\{\{(\w+)\}\}', prompt_content)
        if variables:
            tips.append({
                "type": "info",
                "message": f"检测到 {len(variables)} 个变量：{', '.join(variables)}"
            })
        
        # 检查是否有角色设定
        role_keywords = ['你是', '作为', 'You are', 'As a', '扮演', '角色']
        has_role = any(kw in prompt_content for kw in role_keywords)
        if not has_role:
            tips.append({
                "type": "suggestion",
                "message": "建议添加角色设定，如 '你是一位专业的...'"
            })
            score -= 10
        
        # 检查是否有输出格式要求
        format_keywords = ['格式', '输出', 'format', 'output', 'JSON', 'markdown', '列表', '表格']
        has_format = any(kw.lower() in prompt_content.lower() for kw in format_keywords)
        if not has_format:
            tips.append({
                "type": "suggestion",
                "message": "建议指定输出格式要求"
            })
            score -= 10
        
        # 检查是否有示例
        example_keywords = ['例如', '示例', 'example', 'e.g.', '比如', '如：']
        has_example = any(kw.lower() in prompt_content.lower() for kw in example_keywords)
        if not has_example and len(prompt_content) > 100:
            tips.append({
                "type": "suggestion",
                "message": "考虑添加示例（Few-shot）以提高输出质量"
            })
            score -= 5
        
        return {
            "quick_score": max(0, score),
            "tips": tips,
            "variable_count": len(variables),
            "character_count": len(prompt_content),
            "has_role": has_role,
            "has_format": has_format,
            "has_example": has_example
        }
