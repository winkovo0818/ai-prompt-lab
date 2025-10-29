"""AI 配置 API"""
from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..models.user import User
from ..models.ai_config import AIConfig, AIConfigCreate, AIConfigUpdate, AIConfigResponse
from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..utils.response import success_response, error_response
from ..services.encryption_service import EncryptionService

router = APIRouter()


@router.get("/list")
async def get_ai_configs(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取当前用户的所有 AI 配置（包括全局配置）"""
    # 获取用户自己的配置
    user_configs_statement = select(AIConfig).where(
        AIConfig.user_id == current_user.id,
        AIConfig.is_global == False
    )
    user_configs = db.exec(user_configs_statement).all()
    
    # 获取全局配置
    global_configs_statement = select(AIConfig).where(AIConfig.is_global == True)
    global_configs = db.exec(global_configs_statement).all()
    
    # 合并配置列表：全局配置放在前面
    all_configs = list(global_configs) + list(user_configs)
    
    return success_response(data=[
        AIConfigResponse(
            id=config.id,
            user_id=config.user_id,
            name=config.name,
            base_url=config.base_url,
            api_key=config.api_key,
            model=config.model,
            description=config.description,
            is_default=config.is_default,
            is_global=config.is_global,
            created_at=config.created_at,
            updated_at=config.updated_at
        ) for config in all_configs
    ])


@router.post("/create")
async def create_ai_config(
    data: AIConfigCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """创建 AI 配置"""
    # 检查配置名称是否已存在
    statement = select(AIConfig).where(
        AIConfig.user_id == current_user.id,
        AIConfig.name == data.name
    )
    existing = db.exec(statement).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="配置名称已存在"
        )
    
    # 加密 API Key
    encrypted_api_key = EncryptionService.encrypt_api_key(data.api_key)
    
    # 创建配置
    config = AIConfig(
        user_id=current_user.id,
        name=data.name,
        base_url=data.base_url,
        api_key=encrypted_api_key,  # 使用加密后的 key
        model=data.model,
        description=data.description
    )
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return success_response(
        data=AIConfigResponse(
            id=config.id,
            user_id=config.user_id,
            name=config.name,
            base_url=config.base_url,
            api_key=config.api_key,
            model=config.model,
            description=config.description,
            created_at=config.created_at,
            updated_at=config.updated_at
        ),
        message="创建成功"
    )


@router.put("/{config_id}")
async def update_ai_config(
    config_id: int,
    data: AIConfigUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """更新 AI 配置"""
    # 获取配置
    config = db.get(AIConfig, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    # 检查权限
    if config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改此配置"
        )
    
    # 更新字段
    update_data = data.model_dump(exclude_unset=True)
    
    # 如果更新 API Key，需要加密
    if 'api_key' in update_data and update_data['api_key']:
        # 如果包含*号，说明是脱敏的，不更新
        if '*' not in update_data['api_key']:
            update_data['api_key'] = EncryptionService.encrypt_api_key(update_data['api_key'])
        else:
            # 删除这个字段，不更新
            del update_data['api_key']
    
    for key, value in update_data.items():
        setattr(config, key, value)
    
    config.updated_at = datetime.utcnow()
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return success_response(
        data=AIConfigResponse(
            id=config.id,
            user_id=config.user_id,
            name=config.name,
            base_url=config.base_url,
            api_key=config.api_key,
            model=config.model,
            description=config.description,
            created_at=config.created_at,
            updated_at=config.updated_at
        ),
        message="更新成功"
    )


@router.delete("/{config_id}")
async def delete_ai_config(
    config_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """删除 AI 配置"""
    # 获取配置
    config = db.get(AIConfig, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    # 检查权限
    if config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限删除此配置"
        )
    
    db.delete(config)
    db.commit()
    
    return success_response(message="删除成功")


@router.get("/{config_id}")
async def get_ai_config(
    config_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取单个 AI 配置"""
    config = db.get(AIConfig, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    # 检查权限
    if config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限查看此配置"
        )
    
    return success_response(
        data=AIConfigResponse(
            id=config.id,
            user_id=config.user_id,
            name=config.name,
            base_url=config.base_url,
            api_key=config.api_key,
            model=config.model,
            description=config.description,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
    )


@router.post("/{config_id}/test")
async def test_ai_config(
    config_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """测试 AI 配置连接"""
    from openai import AsyncOpenAI
    import asyncio
    
    # 获取配置
    config = db.get(AIConfig, config_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="配置不存在"
        )
    
    # 检查权限
    if config.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限测试此配置"
        )
    
    try:
        # 创建 OpenAI 客户端（设置 120 秒超时）
        client = AsyncOpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=120.0
        )
        
        # 发送测试请求
        completion = await client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "user", "content": "测试连接，请回复 OK"}
            ],
            max_tokens=10
        )
        
        # 获取响应内容
        response_content = completion.choices[0].message.content
        
        return success_response(
            message="连接测试成功",
            data={
                "status": "success",
                "model": config.model,
                "response": response_content
            }
        )
                
    except Exception as e:
        error_msg = str(e)
        
        # 根据错误类型返回不同的提示
        if "timeout" in error_msg.lower():
            return error_response(
                code=4002,
                message="连接超时，请检查网络或 Base URL 是否正确"
            )
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return error_response(
                code=4001,
                message="认证失败，请检查 API Key 是否正确"
            )
        elif "404" in error_msg or "not found" in error_msg.lower():
            return error_response(
                code=4004,
                message="模型不存在，请检查模型名称是否正确"
            )
        elif "connection" in error_msg.lower():
            return error_response(
                code=4003,
                message="无法连接到服务器，请检查 Base URL 是否正确"
            )
        else:
            return error_response(
                code=4000,
                message=f"测试失败: {error_msg}"
            )


@router.post("/test-connection")
async def test_connection_without_save(
    data: AIConfigCreate,
    current_user: User = Depends(get_current_active_user)
):
    """测试连接（不保存配置）"""
    from openai import AsyncOpenAI
    
    try:
        # 创建 OpenAI 客户端（设置 120 秒超时）
        client = AsyncOpenAI(
            api_key=data.api_key,
            base_url=data.base_url,
            timeout=120.0
        )
        
        # 发送测试请求
        completion = await client.chat.completions.create(
            model=data.model,
            messages=[
                {"role": "user", "content": "测试连接，请回复 OK"}
            ],
            max_tokens=10
        )
        
        # 获取响应内容
        response_content = completion.choices[0].message.content
        
        return success_response(
            message="连接测试成功！配置正确，可以保存",
            data={
                "status": "success",
                "model": data.model,
                "response": response_content
            }
        )
                
    except Exception as e:
        error_msg = str(e)
        
        # 根据错误类型返回不同的提示
        if "timeout" in error_msg.lower():
            return error_response(
                code=4002,
                message="连接超时，请检查网络或 Base URL 是否正确"
            )
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            return error_response(
                code=4001,
                message="认证失败，请检查 API Key 是否正确"
            )
        elif "404" in error_msg or "not found" in error_msg.lower():
            return error_response(
                code=4004,
                message="模型不存在，请检查模型名称是否正确"
            )
        elif "connection" in error_msg.lower():
            return error_response(
                code=4003,
                message="无法连接到服务器，请检查 Base URL 是否正确"
            )
        else:
            return error_response(
                code=4000,
                message=f"测试失败: {error_msg}"
            )

