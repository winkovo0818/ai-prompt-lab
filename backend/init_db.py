"""
数据库初始化脚本
用于创建数据库和表结构
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from app.core.database import create_db_and_tables
from app.models.user import User
from app.models.prompt import Prompt
from app.models.prompt_version import PromptVersion
from app.models.abtest import ABTestResult
from app.models.ai_config import AIConfig


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    try:
        # 创建所有表
        create_db_and_tables()
        print("✓ 数据库表创建成功")
        
        print("\n数据库初始化完成！")
        print("\n提示：")
        print("1. 请确保 MySQL 服务已启动")
        print("2. 请在 .env 文件中配置正确的数据库连接信息")
        print("3. 数据库名称应为: ai_prompt_lab")
        
    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {str(e)}")
        print("\n请检查：")
        print("1. MySQL 服务是否正常运行")
        print("2. 数据库连接配置是否正确")
        print("3. 数据库用户是否有足够的权限")
        sys.exit(1)


if __name__ == "__main__":
    init_database()

