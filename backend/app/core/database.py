from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
from .config import settings

# 导入所有模型确保表被创建
from ..models.abtest import ABTestResult
from ..models.ai_config import AIConfig
from ..models.api_quota import ApiQuota, ApiUsage
from ..models.audit_log import AuditLog, SecurityConfig, SensitiveWord
from ..models.branch import PromptBranch
from ..models.comment import PromptComment
from ..models.commit import PromptCommit
from ..models.execution_history import ExecutionHistory
from ..models.prompt import Prompt, UserPromptFavorite
from ..models.prompt_version import PromptVersion
from ..models.pull_request import PromptPullRequest
from ..models.quality_evaluation import ComparisonReport, QualityEvaluation
from ..models.site_settings import SiteSettings
from ..models.team import Team, TeamInvite, TeamMember, TeamPrompt
from ..models.template import PromptTemplate, TemplateCategory, TemplateRating, UserTemplateFavorite
from ..models.test_suite import PromptTestRun, PromptTestSuite
from ..models.uploaded_file import UploadedFile
from ..models.user import User

# 创建数据库引擎（配置 utf8mb4 支持 emoji）
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={
        "charset": "utf8mb4"
    }
)


def create_db_and_tables():
    """创建数据库表"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
