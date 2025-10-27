"""Prompt 优化 API"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.quality_evaluation import PromptOptimizationRequest, PromptOptimizationResponse
from ..services.evaluation_service import EvaluationService
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/optimization", tags=["Prompt优化"])


@router.post("/analyze", response_model=dict)
async def optimize_prompt(
    request: PromptOptimizationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """AI分析并优化Prompt"""
    
    try:
        result = await EvaluationService.optimize_prompt(
            prompt_content=request.prompt_content,
            optimization_goals=request.optimization_goals,
            db=db,
            user_id=current_user.id
        )
        
        response = PromptOptimizationResponse(
            original_prompt=result["original_prompt"],
            optimized_prompt=result["optimized_prompt"],
            improvements=result["improvements"],
            optimization_suggestions=result["optimization_suggestions"],
            expected_improvement=result["expected_improvement"]
        )
        
        return success_response(data=response.model_dump(), message="Prompt优化完成")
        
    except Exception as e:
        return error_response(code=5002, message=f"优化失败: {str(e)}")

