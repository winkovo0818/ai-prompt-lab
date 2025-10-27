import re
from typing import Dict


def count_tokens(text: str) -> int:
    """
    简单的 Token 计数器（模拟）
    实际项目中应使用 tiktoken 等专业库
    这里使用简化算法：中文字符计2个token，英文单词计1个token
    """
    if not text:
        return 0
    
    # 统计中文字符
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    
    # 统计英文单词（简化处理）
    english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
    
    # 统计数字和符号
    others = len(re.findall(r'[0-9]', text))
    
    # 简单估算
    total_tokens = chinese_chars * 2 + english_words + others // 4
    
    return max(total_tokens, 1)


def estimate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-3.5-turbo") -> float:
    """
    估算API调用成本（美元）
    这里使用模拟价格
    """
    prices = {
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},  # per 1K tokens
        "gpt-4": {"input": 0.03, "output": 0.06},
        "deepseek-chat": {"input": 0.001, "output": 0.002},
    }
    
    price = prices.get(model, prices["gpt-3.5-turbo"])
    
    input_cost = (input_tokens / 1000) * price["input"]
    output_cost = (output_tokens / 1000) * price["output"]
    
    return round(input_cost + output_cost, 6)


def analyze_prompt_complexity(prompt: str) -> Dict[str, any]:
    """分析 Prompt 复杂度"""
    tokens = count_tokens(prompt)
    
    # 检测变量数量
    variables = len(re.findall(r'\{\{[^}]+\}\}', prompt))
    
    # 检测行数
    lines = len(prompt.split('\n'))
    
    # 复杂度评分
    complexity_score = min(100, (tokens // 10) + (variables * 5) + (lines * 2))
    
    return {
        "tokens": tokens,
        "variables": variables,
        "lines": lines,
        "complexity_score": complexity_score
    }

