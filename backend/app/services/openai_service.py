import time
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from sqlmodel import Session, select
from ..utils.token_counter import count_tokens, estimate_cost
from ..models.ai_config import AIConfig


class OpenAIService:
    """
    OpenAI 服务 - 真实 AI 调用
    支持 OpenAI / DeepSeek / Kimi 等兼容 OpenAI API 的模型
    """
    
    @staticmethod
    async def chat_completion(
        prompt: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        **kwargs
    ) -> Dict:
        """
        聊天补全接口 - 真实 AI 调用
        
        Args:
            prompt: 提示词
            model: 模型名称
            temperature: 温度参数
            max_tokens: 最大 token 数
            db: 数据库会话
            user_id: 用户 ID
            **kwargs: 其他参数
        
        Returns:
            包含响应内容和统计信息的字典
        """
        # 获取用户的 AI 配置
        if not db or not user_id:
            raise ValueError("需要提供 db 和 user_id 参数")
        
        # 1. 查询用户配置的 AI Config（优先使用默认配置）
        statement = select(AIConfig).where(
            AIConfig.user_id == user_id,
            AIConfig.is_default == True
        ).limit(1)
        ai_config = db.exec(statement).first()
        
        # 2. 如果没有默认配置，查找任意用户配置
        if not ai_config:
            statement = select(AIConfig).where(AIConfig.user_id == user_id).limit(1)
            ai_config = db.exec(statement).first()
        
        # 3. 如果用户没有配置，查找全局配置（管理员配置的 is_global=True）
        if not ai_config:
            statement = select(AIConfig).where(AIConfig.is_global == True).limit(1)
            ai_config = db.exec(statement).first()
        
        # 4. 如果还是没有，尝试从环境变量读取
        if not ai_config:
            from ..core.config import settings
            if settings.ENABLE_DEFAULT_AI and settings.DEFAULT_AI_API_KEY:
                # 使用环境变量配置（临时对象）
                ai_config = type('DefaultAIConfig', (), {
                    'api_key': settings.DEFAULT_AI_API_KEY,
                    'base_url': settings.DEFAULT_AI_BASE_URL,
                    'model': settings.DEFAULT_AI_MODEL,
                    'provider': settings.DEFAULT_AI_PROVIDER,
                    'name': '环境变量配置',
                    'is_encrypted': False  # 环境变量的 key 不需要解密
                })()
            else:
                raise ValueError("未找到 AI 配置，请先在设置页面添加 AI 配置")
        
        # 解密 API Key（数据库中的 key 是加密存储的）
        api_key = ai_config.api_key
        if hasattr(ai_config, 'id') and ai_config.id:  # 数据库中的配置需要解密
            from ..services.encryption_service import EncryptionService
            try:
                api_key = EncryptionService.decrypt_api_key(ai_config.api_key)
                print(f"[DEBUG] AI 配置解密成功: {ai_config.name}, Key 长度: {len(api_key)}")
            except Exception as e:
                print(f"[ERROR] API Key 解密失败: {str(e)}")
                raise ValueError(f"API Key 解密失败: {str(e)}")
        
        # 创建 OpenAI 客户端
        client = AsyncOpenAI(
            api_key=api_key,  # 使用解密后的 key
            base_url=ai_config.base_url,
            timeout=600000  
        )
        
        try:
            # 调用真实 AI
            start_time = time.time()
            
            # 构建消息列表
            messages = []
            
            # 如果提供了 system_prompt，添加系统消息
            system_prompt = kwargs.get("system_prompt")
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            completion = await client.chat.completions.create(
                model=ai_config.model,  # 使用配置中的模型
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_time = time.time() - start_time
            
            # 提取响应内容
            output_text = completion.choices[0].message.content or ""
            
            # 获取 token 使用情况
            input_tokens = completion.usage.prompt_tokens if completion.usage else count_tokens(prompt)
            output_tokens = completion.usage.completion_tokens if completion.usage else count_tokens(output_text)
            total_tokens = completion.usage.total_tokens if completion.usage else (input_tokens + output_tokens)
            
            # 估算成本
            cost = estimate_cost(input_tokens, output_tokens, ai_config.model)
            
            return {
                "output": output_text,
                "content": output_text,  # 兼容字段
                "model": ai_config.model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
                "cost": cost,
                "finish_reason": completion.choices[0].finish_reason if completion.choices else "stop",
                "response_time": round(response_time, 3)
            }
            
        except Exception as e:
            # 处理错误
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                raise ValueError("AI 调用超时，请检查网络连接")
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                raise ValueError("API Key 无效，请检查 AI 配置")
            elif "404" in error_msg or "not found" in error_msg.lower():
                raise ValueError("模型不存在，请检查 AI 配置中的模型名称")
            elif "rate_limit" in error_msg.lower():
                raise ValueError("API 调用频率超限，请稍后再试")
            else:
                raise ValueError(f"AI 调用失败: {error_msg}")
    
    @staticmethod
    async def batch_completion(
        prompts: List[str],
        model: str = "gpt-3.5-turbo",
        db: Optional[Session] = None,
        user_id: Optional[int] = None,
        **kwargs
    ) -> List[Dict]:
        """
        批量完成请求
        
        Args:
            prompts: Prompt 列表
            model: 模型名称
            db: 数据库会话
            user_id: 用户 ID
            **kwargs: 其他参数
        
        Returns:
            响应列表
        """
        results = []
        
        for prompt in prompts:
            result = await OpenAIService.chat_completion(
                prompt=prompt,
                model=model,
                db=db,
                user_id=user_id,
                **kwargs
            )
            results.append(result)
        
        return results
    
    @staticmethod
    def get_available_models(db: Session, user_id: int) -> List[Dict[str, str]]:
        """获取用户配置的可用模型列表（包括全局配置）"""
        print(f"[DEBUG] 查询用户 {user_id} 的 AI 配置...")
        
        # 查询用户自己的配置
        user_statement = select(AIConfig).where(
            AIConfig.user_id == user_id,
            AIConfig.is_global == False
        )
        user_configs = db.exec(user_statement).all()
        
        # 查询全局配置
        global_statement = select(AIConfig).where(AIConfig.is_global == True)
        global_configs = db.exec(global_statement).all()
        
        # 合并配置：全局配置在前
        all_configs = list(global_configs) + list(user_configs)
        
        print(f"[DEBUG] 找到 {len(global_configs)} 个全局配置, {len(user_configs)} 个用户配置")
        for config in all_configs:
            print(f"[DEBUG] - {config.name}: {config.model} (全局: {config.is_global})")
        
        models = []
        for config in all_configs:
            model_name = config.name
            # 为全局配置添加标识
            if config.is_global:
                model_name = f"{config.name} [全局]"
            
            models.append({
                "id": config.model,
                "name": model_name,
                "description": config.description or f"{config.name} - {config.model}",
                "provider": "Custom",
                "base_url": config.base_url,
                "is_global": config.is_global
            })
        
        print(f"[DEBUG] 返回模型列表: {models}")
        return models

