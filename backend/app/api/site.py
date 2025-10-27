from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from ..core.database import get_session
from ..models.site_settings import SiteSettings
from ..utils.response import success_response

router = APIRouter(prefix="/api/site", tags=["网站"])


@router.get("/settings", response_model=dict)
async def get_public_site_settings(db: Session = Depends(get_session)):
    """获取网站公开设置（无需登录）"""
    settings = db.exec(select(SiteSettings)).first()
    
    if not settings:
        # 如果没有设置记录，创建默认设置
        settings = SiteSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    # 只返回公开信息
    return success_response(data={
        "siteName": settings.site_name,
        "siteDescription": settings.site_description,
        "siteKeywords": settings.site_keywords,
        "allowRegister": settings.allow_register,
        "enableMarket": settings.enable_market
    })

