from typing import Optional, Dict
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, JSON, Text


class ExecutionHistory(SQLModel, table=True):
    """执行历史记录模型"""
    __tablename__ = "execution_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    prompt_id: Optional[int] = Field(default=None, foreign_key="prompts.id", index=True)
    
    # Prompt 相关信息
    prompt_content: str = Field(sa_column=Column(Text))
    prompt_version: int = Field(default=1)  # 记录执行时的 prompt 版本
    variables: Optional[Dict[str, str]] = Field(default=None, sa_column=Column(JSON))
    final_prompt: str = Field(sa_column=Column(Text))  # 替换变量后的最终 prompt
    
    # 模型配置
    model: str = Field(max_length=100)
    temperature: float = Field(default=0.7)
    max_tokens: int = Field(default=2000)
    
    # 执行结果
    output: str = Field(sa_column=Column(Text))
    input_tokens: int = Field(default=0)
    output_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    cost: float = Field(default=0.0)
    response_time: float = Field(default=0.0)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ExecutionHistoryResponse(SQLModel):
    """执行历史响应模型"""
    id: int
    user_id: int
    prompt_id: Optional[int] = None
    
    prompt_content: str
    prompt_version: int
    variables: Optional[Dict[str, str]] = None
    final_prompt: str
    
    model: str
    temperature: float
    max_tokens: int
    
    output: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    response_time: float
    
    created_at: datetime
    is_cached: bool = True  # 标识这是历史记录

