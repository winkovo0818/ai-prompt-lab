from typing import Optional, Dict, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Text


class QualityEvaluation(SQLModel, table=True):
    """AI质量评测结果模型"""
    __tablename__ = "quality_evaluations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    # 关联的测试（可能是A/B测试或批量测试）
    test_type: str = Field(max_length=50)  # "abtest", "batch", "single"
    test_id: Optional[int] = Field(default=None, index=True)
    
    # 被评测的内容
    prompt_id: Optional[int] = Field(default=None, foreign_key="prompts.id")
    prompt_content: str = Field(sa_column=Column(Text))
    output_content: str = Field(sa_column=Column(Text))
    
    # AI评分维度
    accuracy_score: float = Field(default=0.0)  # 准确性 (0-10)
    relevance_score: float = Field(default=0.0)  # 相关性 (0-10)
    fluency_score: float = Field(default=0.0)  # 流畅度 (0-10)
    creativity_score: float = Field(default=0.0)  # 创意性 (0-10)
    safety_score: float = Field(default=0.0)  # 安全性 (0-10)
    overall_score: float = Field(default=0.0)  # 综合评分 (0-10)
    
    # 详细评价
    evaluation_details: Dict = Field(default={}, sa_column=Column(JSON))
    
    # 安全性检测
    safety_issues: List[str] = Field(default=[], sa_column=Column(JSON))
    has_sensitive_content: bool = Field(default=False)
    
    # 性能指标
    response_time: float = Field(default=0.0)  # 响应时间（秒）
    token_count: int = Field(default=0)  # Token消耗
    cost: float = Field(default=0.0)  # 成本
    cost_efficiency_score: float = Field(default=0.0)  # 成本效益评分
    
    # AI分析和建议
    strengths: List[str] = Field(default=[], sa_column=Column(JSON))  # 优点
    weaknesses: List[str] = Field(default=[], sa_column=Column(JSON))  # 缺点
    suggestions: List[str] = Field(default=[], sa_column=Column(JSON))  # 改进建议
    
    # 元数据
    evaluation_model: str = Field(max_length=100)  # 用于评测的AI模型
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BatchTestResult(SQLModel, table=True):
    """批量测试结果模型"""
    __tablename__ = "batch_test_results"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    test_name: str = Field(max_length=200)
    prompt_id: int = Field(foreign_key="prompts.id")
    
    # 测试输入数据集
    test_cases: List[Dict] = Field(sa_column=Column(JSON))  # [{variables: {...}, expected_output: "..."}]
    
    # 测试结果
    results: List[Dict] = Field(sa_column=Column(JSON))  # 每个测试用例的结果
    
    # 统计数据
    total_cases: int = Field(default=0)
    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    
    # 平均性能指标
    avg_response_time: float = Field(default=0.0)
    avg_token_count: int = Field(default=0)
    avg_cost: float = Field(default=0.0)
    avg_quality_score: float = Field(default=0.0)
    
    # 模型配置
    model: str = Field(max_length=100)
    temperature: float = Field(default=0.7)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class ComparisonReport(SQLModel, table=True):
    """对比分析报告模型"""
    __tablename__ = "comparison_reports"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    abtest_id: int = Field(foreign_key="abtest_results.id", index=True)
    
    # 对比分析数据
    winner_prompt_id: Optional[int] = None  # 获胜的Prompt ID
    winner_reason: str = Field(default="", sa_column=Column(Text))
    
    # 详细对比
    comparison_data: Dict = Field(default={}, sa_column=Column(JSON))
    
    # 图表数据
    chart_data: Dict = Field(default={}, sa_column=Column(JSON))
    
    # AI生成的分析报告
    summary: str = Field(sa_column=Column(Text))
    recommendations: List[str] = Field(default=[], sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ============ 请求/响应模型 ============

class QualityEvaluationRequest(SQLModel):
    """质量评测请求"""
    output_content: str
    prompt_content: Optional[str] = None
    evaluation_criteria: Optional[List[str]] = None  # 自定义评测维度


class QualityEvaluationResponse(SQLModel):
    """质量评测响应"""
    id: int
    accuracy_score: float
    relevance_score: float
    fluency_score: float
    creativity_score: float
    safety_score: float
    overall_score: float
    evaluation_details: Dict
    safety_issues: List[str]
    has_sensitive_content: bool
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    created_at: datetime


class BatchTestRequest(SQLModel):
    """批量测试请求"""
    test_name: str
    prompt_id: int
    test_cases: List[Dict]  # [{variables: {...}, expected_output: "..."}]
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    enable_evaluation: bool = True  # 是否启用AI评测


class BatchTestResponse(SQLModel):
    """批量测试响应"""
    id: int
    test_name: str
    prompt_id: int
    total_cases: int
    success_count: int
    failure_count: int
    avg_response_time: float
    avg_token_count: int
    avg_cost: float
    avg_quality_score: float
    results: List[Dict]
    created_at: datetime
    completed_at: Optional[datetime]


class ComparisonReportResponse(SQLModel):
    """对比报告响应"""
    id: int
    abtest_id: int
    winner_prompt_id: Optional[int]
    winner_reason: str
    comparison_data: List[Dict]
    chart_data: Dict
    summary: str
    recommendations: List[str]
    created_at: datetime


class PromptOptimizationRequest(SQLModel):
    """Prompt优化请求"""
    prompt_content: str
    optimization_goals: Optional[List[str]] = None  # ["clarity", "specificity", "effectiveness"]


class PromptOptimizationResponse(SQLModel):
    """Prompt优化响应"""
    original_prompt: str
    optimized_prompt: str
    improvements: List[Dict]  # [{"aspect": "clarity", "before": "...", "after": "...", "reason": "..."}]
    optimization_suggestions: List[str]
    expected_improvement: str

