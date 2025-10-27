"""系统配置管理API"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Dict, Any

from ..core.deps import get_db, get_current_admin_user
from ..models.user import User
from ..models.ai_config import AIConfig, AIConfigCreate
from ..services.encryption_service import EncryptionService

router = APIRouter(prefix="/api/system", tags=["系统配置"])


class GlobalAIConfigResponse:
    """全局AI配置响应（简化版）"""
    pass


@router.get("/global-ai-config")
def get_global_ai_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """获取全局AI配置（仅管理员）- 从 ai_configs 表中查询 is_global=True 的配置"""
    # 查找全局配置
    statement = select(AIConfig).where(AIConfig.is_global == True).limit(1)
    global_config = db.exec(statement).first()
    
    # 调试日志
    print(f"[DEBUG] 全局配置查询结果: {global_config}")
    if global_config:
        print(f"[DEBUG] 全局配置详情: ID={global_config.id}, Name={global_config.name}, Model={global_config.model}, is_global={global_config.is_global}")
    
    if global_config:
        # API Key 脱敏显示
        api_key = global_config.api_key
        if api_key and len(api_key) > 8:
            masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
        else:
            masked_key = "****"
        
        result_data = {
            "code": 0,
            "data": {
                "id": global_config.id,
                "enable_default_ai": True,
                "default_ai_model": global_config.model,
                "default_ai_api_key": masked_key,
                "default_ai_base_url": global_config.base_url,
                "has_api_key": True,
                "name": global_config.name,
                "description": global_config.description
            }
        }
        print(f"[DEBUG] 返回数据: {result_data}")
        return result_data
    else:
        # 没有全局配置
        result_data = {
            "code": 0,
            "data": {
                "id": None,
                "enable_default_ai": False,
                "default_ai_model": "gpt-3.5-turbo",
                "default_ai_api_key": None,
                "default_ai_base_url": "https://api.openai.com/v1",
                "has_api_key": False,
                "name": "",
                "description": ""
            }
        }
        print(f"[DEBUG] 返回数据(无全局配置): {result_data}")
        return result_data


@router.put("/global-ai-config")
def update_global_ai_config(
    config_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """更新全局AI配置（仅管理员）- 在 ai_configs 表中创建或更新 is_global=True 的配置"""
    try:
        # 查找现有的全局配置
        statement = select(AIConfig).where(AIConfig.is_global == True).limit(1)
        global_config = db.exec(statement).first()
        
        enable_default_ai = config_data.get("enable_default_ai", True)
        
        if not enable_default_ai:
            # 禁用全局AI - 删除全局配置
            if global_config:
                db.delete(global_config)
                db.commit()
            
            # 记录审计日志
            from ..services.audit_service import AuditService
            AuditService.log(
                db=db,
                user_id=current_user.id,
                action="disable_global_ai",
                resource="ai_config",
                description="禁用全局AI配置",
                resource_id=global_config.id if global_config else 0
            )
            
            return {
                "code": 0,
                "message": "已禁用全局AI配置",
                "data": {"enable_default_ai": False}
            }
        
        # 启用全局AI - 创建或更新配置
        name = config_data.get("name", "全局默认AI")
        model = config_data.get("default_ai_model", "gpt-3.5-turbo")
        base_url = config_data.get("default_ai_base_url", "https://api.openai.com/v1")
        api_key = config_data.get("default_ai_api_key", "")
        description = config_data.get("description", "系统默认AI配置，供未配置AI的用户使用")
        
        # 如果API Key包含*，说明是脱敏的，不更新
        if api_key and "*" in api_key:
            api_key = None
        
        # 如果提供了新的API Key，加密存储
        if api_key:
            api_key = EncryptionService.encrypt_api_key(api_key)
        
        if global_config:
            # 更新现有配置
            global_config.name = name
            global_config.model = model
            global_config.base_url = base_url
            global_config.description = description
            if api_key:  # 只在提供新key时更新
                global_config.api_key = api_key
            global_config.updated_at = db.exec(select(AIConfig).where(AIConfig.id == global_config.id)).first().updated_at
            
            db.add(global_config)
            db.commit()
            db.refresh(global_config)
            
            action = "update_global_ai"
            message = "全局AI配置更新成功"
        else:
            # 创建新的全局配置
            if not api_key:
                raise HTTPException(status_code=400, detail="首次创建全局AI配置必须提供API Key")
            
            global_config = AIConfig(
                user_id=current_user.id,  # 记录创建者
                name=name,
                model=model,
                base_url=base_url,
                api_key=api_key,
                description=description,
                is_global=True,
                is_default=False
            )
            
            db.add(global_config)
            db.commit()
            db.refresh(global_config)
            
            action = "create_global_ai"
            message = "全局AI配置创建成功"
        
        # 记录审计日志
        from ..services.audit_service import AuditService
        AuditService.log(
            db=db,
            user_id=current_user.id,
            action=action,
            resource="ai_config",
            resource_id=global_config.id,
            description=f"{message}: {model} @ {base_url}",
            ip_address="",
            user_agent=""
        )
        
        return {
            "code": 0,
            "message": message,
            "data": {
                "id": global_config.id,
                "enable_default_ai": True
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/global-ai-config/test")
async def test_global_ai_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """测试全局AI配置（仅管理员）- 测试 ai_configs 表中 is_global=True 的配置"""
    try:
        # 查找全局配置
        statement = select(AIConfig).where(AIConfig.is_global == True).limit(1)
        global_config = db.exec(statement).first()
        
        if not global_config:
            raise HTTPException(status_code=400, detail="未配置全局AI")
        
        print(f"[DEBUG] 测试全局配置: Model={global_config.model}, Base URL={global_config.base_url}")
        
        # 解密API Key
        try:
            api_key = EncryptionService.decrypt_api_key(global_config.api_key)
            print(f"[DEBUG] API Key 解密成功，长度: {len(api_key) if api_key else 0}")
        except Exception as e:
            print(f"[ERROR] API Key 解密失败: {str(e)}")
            raise HTTPException(status_code=500, detail=f"API Key 解密失败: {str(e)}")
        
        # 测试调用
        from openai import AsyncOpenAI
        import httpx
        
        # 创建带超时的 httpx 客户端
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, connect=10.0)  # 总超时30秒，连接超时10秒
        )
        
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=global_config.base_url,
            http_client=http_client
        )
        
        print(f"[DEBUG] 开始调用 AI API...")
        response = await client.chat.completions.create(
            model=global_config.model,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=10
        )
        print(f"[DEBUG] AI API 调用成功")
        
        # 关闭 http 客户端
        await http_client.aclose()
        
        return {
            "code": 0,
            "message": "全局AI配置测试成功",
            "data": {
                "model": global_config.model,
                "base_url": global_config.base_url,
                "response": response.choices[0].message.content or "OK"
            }
        }
    
    except HTTPException:
        raise
    except httpx.TimeoutException as e:
        print(f"[ERROR] API 调用超时: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"API 调用超时，请检查网络连接和 Base URL 配置是否正确。错误: {str(e)}"
        )
    except httpx.ConnectError as e:
        print(f"[ERROR] 无法连接到 API: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"无法连接到 API 服务器，请检查 Base URL 是否正确。错误: {str(e)}"
        )
    except Exception as e:
        print(f"[ERROR] 测试失败: {type(e).__name__}: {str(e)}")
        error_msg = str(e)
        
        # 提供更友好的错误提示
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            detail = f"API Key 验证失败，请检查 API Key 是否正确。错误: {error_msg}"
        elif "model" in error_msg.lower():
            detail = f"模型不存在或不可用，请检查模型名称是否正确。错误: {error_msg}"
        else:
            detail = f"测试失败: {error_msg}"
        
        raise HTTPException(status_code=500, detail=detail)

