import time
import re
from typing import Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..models.user import User
from ..models.prompt import Prompt
from ..models.execution_history import ExecutionHistory
from ..models.uploaded_file import UploadedFile
from ..services.openai_service import OpenAIService
from ..services.rate_limit import rate_limiter
from ..services.file_service import FileService
from ..utils.response import success_response, error_response
from ..utils.token_counter import count_tokens, analyze_prompt_complexity

router = APIRouter(prefix="/api/run", tags=["执行Prompt"])


class RunPromptRequest(BaseModel):
    """执行 Prompt 请求模型"""
    prompt_id: Optional[int] = None
    prompt_content: Optional[str] = None
    variables: Optional[Dict[str, str]] = None
    file_variables: Optional[Dict[str, int]] = None  # 文件变量：{变量名: 文件ID}
    model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2000


def replace_variables(content: str, variables: Dict[str, str]) -> str:
    """替换 Prompt 中的变量"""
    if not variables:
        return content
    
    result = content
    for key, value in variables.items():
        # 支持 {{变量名}} 格式
        pattern = r'\{\{\s*' + re.escape(key) + r'\s*\}\}'
        result = re.sub(pattern, value, result)
    
    return result


@router.post("", response_model=dict)
async def run_prompt(
    request: RunPromptRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """执行单个 Prompt"""
    
    # 检查频率限制
    allowed, error_msg = rate_limiter.check_rate_limit(current_user.id)
    if not allowed:
        return error_response(code=3001, message=error_msg)
    
    # 获取 Prompt 内容
    prompt_content = ""
    prompt_title = "临时 Prompt"
    
    if request.prompt_id:
        # 从数据库加载
        prompt = db.get(Prompt, request.prompt_id)
        if not prompt:
            return error_response(code=2001, message="Prompt 不存在")
        
        # 权限检查
        if prompt.user_id != current_user.id and not prompt.is_public:
            return error_response(code=2002, message="无权访问该 Prompt")
        
        prompt_content = prompt.content
        prompt_title = prompt.title
    
    elif request.prompt_content:
        # 使用临时内容
        prompt_content = request.prompt_content
    
    else:
        return error_response(code=3002, message="必须提供 prompt_id 或 prompt_content")
    
    # 处理文件变量
    all_variables = dict(request.variables or {})
    
    if request.file_variables:
        for var_name, file_id in request.file_variables.items():
            # 获取文件
            uploaded_file = db.get(UploadedFile, file_id)
            
            if not uploaded_file or uploaded_file.is_deleted:
                return error_response(code=3004, message=f"文件不存在: {var_name}")
            
            # 权限检查
            if uploaded_file.user_id != current_user.id:
                return error_response(code=3005, message=f"无权访问文件: {var_name}")
            
            # 根据文件类型处理
            if uploaded_file.file_type in ['text', 'code']:
                # 文本文件：使用提取的文本
                all_variables[var_name] = uploaded_file.extracted_text or ""
            
            elif uploaded_file.file_type == 'image':
                # 图片：转为 Base64（用于 GPT-4V 等视觉模型）
                base64_data = FileService.image_to_base64(uploaded_file.file_path)
                if base64_data:
                    all_variables[var_name] = base64_data
                else:
                    all_variables[var_name] = f"[图片: {uploaded_file.filename}]"
            
            elif uploaded_file.file_type == 'document':
                # 文档：使用提取的文本
                all_variables[var_name] = uploaded_file.extracted_text or f"[文档: {uploaded_file.filename}]"
            
            else:
                # 其他：显示文件信息
                all_variables[var_name] = f"[文件: {uploaded_file.filename}, 大小: {uploaded_file.file_size} 字节]"
    
    # 替换变量
    final_prompt = replace_variables(prompt_content, all_variables)
    
    # 分析 Prompt 复杂度
    complexity = analyze_prompt_complexity(final_prompt)
    
    # 记录开始时间
    start_time = time.time()
    
    # 调用模型
    try:
        result = await OpenAIService.chat_completion(
            prompt=final_prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            db=db,
            user_id=current_user.id
        )
    except ValueError as e:
        return error_response(code=3003, message=str(e))
    except Exception as e:
        return error_response(code=3003, message=f"模型调用失败: {str(e)}")
    
    # 计算响应时间
    response_time = time.time() - start_time
    
    # 记录请求
    rate_limiter.record_request(current_user.id)
    
    # 保存执行历史
    try:
        execution_history = ExecutionHistory(
            user_id=current_user.id,
            prompt_id=request.prompt_id,
            prompt_content=prompt_content,
            prompt_version=prompt.version if request.prompt_id and prompt else 1,
            variables=request.variables,
            final_prompt=final_prompt,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            output=result["output"],
            input_tokens=result["input_tokens"],
            output_tokens=result["output_tokens"],
            total_tokens=result["total_tokens"],
            cost=result["cost"],
            response_time=round(response_time, 3)
        )
        db.add(execution_history)
        db.commit()
        print(f"✅ 执行历史已保存 (ID: {execution_history.id})")
    except Exception as e:
        print(f"⚠️ 保存执行历史失败: {str(e)}")
        # 不影响主流程，继续返回结果
    
    # 构造响应
    response_data = {
        "prompt_title": prompt_title,
        "prompt_content": prompt_content,
        "final_prompt": final_prompt,
        "variables": request.variables,
        "output": result["output"],
        "model": result["model"],
        "input_tokens": result["input_tokens"],
        "output_tokens": result["output_tokens"],
        "total_tokens": result["total_tokens"],
        "cost": result["cost"],
        "response_time": round(response_time, 3),
        "complexity": complexity,
        "is_cached": False  # 新执行的结果
    }
    
    return success_response(data=response_data, message="执行成功")


@router.get("/models", response_model=dict)
async def get_available_models(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取可用的模型列表"""
    print(f"[DEBUG] /api/run/models 被调用")
    print(f"[DEBUG] 用户: {current_user.username} (ID: {current_user.id})")
    
    models = OpenAIService.get_available_models(db, current_user.id)
    
    print(f"[DEBUG] 返回 {len(models)} 个模型")
    return success_response(data=models)


@router.get("/usage", response_model=dict)
async def get_usage_stats(
    current_user: User = Depends(get_current_active_user)
):
    """获取用户的 API 使用统计"""
    
    stats = rate_limiter.get_usage_stats(current_user.id)
    
    return success_response(data=stats)

