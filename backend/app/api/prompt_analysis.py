"""
Prompt 分析 API
提供 Prompt 质量分析和优化建议
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlmodel import Session

from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..services.prompt_analyzer import PromptAnalyzer

router = APIRouter(prefix="/analysis", tags=["Prompt 分析"])


class AnalyzeRequest(BaseModel):
    """分析请求"""
    content: str
    title: Optional[str] = None


class QuickAnalyzeRequest(BaseModel):
    """快速分析请求"""
    content: str


@router.post("/analyze")
async def analyze_prompt(
    request: AnalyzeRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    使用 AI 分析 Prompt 质量
    
    返回详细的评分、优缺点、改进建议和优化后的 Prompt
    """
    if not request.content or len(request.content.strip()) < 5:
        raise HTTPException(status_code=400, detail="Prompt 内容过短")
    
    result = await PromptAnalyzer.analyze(
        prompt_content=request.content,
        db=db,
        user_id=current_user.id,
        prompt_title=request.title
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500, 
            detail=result.get("error", "分析失败")
        )
    
    return {
        "code": 0,
        "data": result,
        "message": "分析成功"
    }


@router.post("/quick")
async def quick_analyze(
    request: QuickAnalyzeRequest,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    快速本地分析 Prompt（不调用 AI）
    
    返回基本的格式检查和建议
    """
    if not request.content:
        raise HTTPException(status_code=400, detail="Prompt 内容不能为空")
    
    # 重新获取用户避免会话冲突
    user = db.get(User, current_user.id)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    result = PromptAnalyzer.get_quick_tips(request.content)
    return {
        "code": 0,
        "data": {
            "success": True,
            "analysis": result
        },
        "message": "分析成功"
    }
