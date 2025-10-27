from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ..core.database import get_session
from ..core.security import verify_password, get_password_hash, create_access_token
from ..core.config import settings
from ..core.deps import get_current_active_user
from ..models.user import User, UserCreate, UserLogin, Token, UserResponse, UserProfileUpdate
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=dict)
async def register(user_data: UserCreate, db: Session = Depends(get_session)):
    """用户注册"""
    
    # 检查用户名是否已存在
    statement = select(User).where(User.username == user_data.username)
    existing_user = db.exec(statement).first()
    if existing_user:
        return error_response(code=1001, message="用户名已存在")
    
    # 检查邮箱是否已存在
    statement = select(User).where(User.email == user_data.email)
    existing_email = db.exec(statement).first()
    if existing_email:
        return error_response(code=1002, message="邮箱已被注册")
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 生成 token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id)}, expires_delta=access_token_expires
    )
    
    # 构造响应
    user_response = UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        api_key=new_user.api_key,
        role=new_user.role,
        nickname=new_user.nickname,
        phone=new_user.phone,
        avatar_url=new_user.avatar_url,
        bio=new_user.bio,
        company=new_user.company,
        location=new_user.location,
        website=new_user.website,
        last_login_at=new_user.last_login_at,
        login_count=new_user.login_count,
        is_active=new_user.is_active,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )
    
    token_data = Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )
    
    return success_response(data=token_data.model_dump(), message="注册成功")


@router.post("/login", response_model=dict)
async def login(login_data: UserLogin, db: Session = Depends(get_session)):
    """用户登录"""
    
    # 查找用户
    statement = select(User).where(User.username == login_data.username)
    user = db.exec(statement).first()
    
    if not user:
        return error_response(code=1003, message="用户名或密码错误")
    
    # 验证密码
    if not verify_password(login_data.password, user.hashed_password):
        return error_response(code=1003, message="用户名或密码错误")
    
    # 检查用户是否激活
    if not user.is_active:
        return error_response(code=1004, message="账户已被禁用")
    
    # 生成 token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    # 构造响应
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        api_key=user.api_key,
        role=user.role,
        nickname=user.nickname,
        phone=user.phone,
        avatar_url=user.avatar_url,
        bio=user.bio,
        company=user.company,
        location=user.location,
        website=user.website,
        last_login_at=user.last_login_at,
        login_count=user.login_count,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    token_data = Token(
        access_token=access_token,
        token_type="bearer",
        user=user_response
    )
    
    return success_response(data=token_data.model_dump(), message="登录成功")


@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前用户信息"""
    
    user_response = UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        api_key=current_user.api_key,
        role=current_user.role,
        nickname=current_user.nickname,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        company=current_user.company,
        location=current_user.location,
        website=current_user.website,
        last_login_at=current_user.last_login_at,
        login_count=current_user.login_count,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    
    return success_response(data=user_response.model_dump())


@router.put("/api-key", response_model=dict)
async def update_api_key(
    api_key: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """更新用户的 API Key"""
    
    current_user.api_key = api_key
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return success_response(message="API Key 更新成功")


@router.put("/profile", response_model=dict)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """更新个人资料"""
    from datetime import datetime
    
    # 更新邮箱
    if profile_data.email:
        # 检查邮箱是否已被使用
        existing = db.exec(
            select(User).where(User.email == profile_data.email, User.id != current_user.id)
        ).first()
        if existing:
            return error_response(code=1002, message="邮箱已被使用")
        current_user.email = profile_data.email
    
    # 更新密码
    if profile_data.password:
        current_user.hashed_password = get_password_hash(profile_data.password)
    
    # 更新其他个人资料字段
    if profile_data.nickname is not None:
        current_user.nickname = profile_data.nickname
    if profile_data.phone is not None:
        # 检查手机号是否已被使用
        if profile_data.phone:
            existing = db.exec(
                select(User).where(User.phone == profile_data.phone, User.id != current_user.id)
            ).first()
            if existing:
                return error_response(code=1005, message="手机号已被使用")
        current_user.phone = profile_data.phone
    if profile_data.bio is not None:
        current_user.bio = profile_data.bio
    if profile_data.company is not None:
        current_user.company = profile_data.company
    if profile_data.location is not None:
        current_user.location = profile_data.location
    if profile_data.website is not None:
        current_user.website = profile_data.website
    
    current_user.updated_at = datetime.utcnow()
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    user_response = UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        api_key=current_user.api_key,
        role=current_user.role,
        nickname=current_user.nickname,
        phone=current_user.phone,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        company=current_user.company,
        location=current_user.location,
        website=current_user.website,
        last_login_at=current_user.last_login_at,
        login_count=current_user.login_count,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    
    return success_response(data=user_response.model_dump(), message="个人资料更新成功")

