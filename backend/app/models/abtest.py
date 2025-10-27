from typing import Optional, List, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, JSON, Column


class ABTestResult(SQLModel, table=True):
    """A/B 测试结果模型"""
    __tablename__ = "abtest_results"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    
    test_name: str = Field(max_length=200)
    input_variables: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    
    # 测试的 Prompt IDs
    prompt_ids: List[int] = Field(sa_column=Column(JSON))
    
    # 测试结果（每个 Prompt 的响应时间、token 数、输出等）
    results: List[Dict] = Field(sa_column=Column(JSON))
    
    # 可选的质量评分
    quality_scores: Optional[Dict] = Field(default=None, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ABTestCreate(SQLModel):
    """创建 A/B 测试模型"""
    test_name: str = Field(max_length=200)
    prompt_ids: List[int] = Field(min_items=2)
    input_variables: Optional[Dict] = None
    model: str = "gpt-3.5-turbo"
    enable_evaluation: bool = True  # 是否启用AI评测
    generate_report: bool = True  # 是否生成对比报告


class ABTestResponse(SQLModel):
    """A/B 测试响应模型"""
    id: int
    user_id: int
    test_name: str
    input_variables: Optional[Dict] = None
    prompt_ids: List[int]
    results: List[Dict]
    quality_scores: Optional[Dict] = None
    created_at: datetime


class PromptExecutionResult(SQLModel):
    """单个 Prompt 执行结果"""
    prompt_id: int
    prompt_title: str
    output: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    response_time: float
    model: str
    cost: float

