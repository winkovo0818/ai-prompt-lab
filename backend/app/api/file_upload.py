"""文件上传 API"""
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlmodel import Session, select

from ..models.user import User
from ..models.uploaded_file import UploadedFile, UploadedFileResponse
from ..core.database import get_session
from ..core.deps import get_current_active_user
from ..services.file_service import FileService
from ..utils.response import success_response, error_response

router = APIRouter(prefix="/api/files", tags=["文件上传"])


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """
    上传文件
    
    支持的文件类型：
    - 图片：.jpg, .jpeg, .png, .gif, .webp
    - 文本：.txt, .md, .csv, .json, .xml
    - 文档：.pdf, .doc, .docx
    - 代码：.py, .js, .ts, .java, .cpp, .c, .go, .rs
    """
    # 检查文件名
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件名不能为空"
        )
    
    # 检查文件类型
    if not FileService.is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型。支持的文件类型：图片、文本、文档、代码"
        )
    
    # 读取文件内容
    file_content = await file.read()
    
    # 检查文件大小
    if len(file_content) > FileService.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 {FileService.MAX_FILE_SIZE / 1024 / 1024}MB）"
        )
    
    # 保存文件
    try:
        file_path, file_type = FileService.save_file(
            file_content,
            file.filename,
            current_user.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 处理文件（提取内容）
    processed = FileService.process_file(file_path, file_type)
    
    # 保存到数据库
    uploaded_file = UploadedFile(
        user_id=current_user.id,
        filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        mime_type=file.content_type or 'application/octet-stream',
        file_size=len(file_content),
        extracted_text=processed.get('text_content')
    )
    
    db.add(uploaded_file)
    db.commit()
    db.refresh(uploaded_file)
    
    # 构造响应
    response = UploadedFileResponse(
        id=uploaded_file.id,
        filename=uploaded_file.filename,
        file_type=uploaded_file.file_type,
        file_size=uploaded_file.file_size,
        text_content=processed.get('text_content'),
        created_at=uploaded_file.created_at
    )
    
    # 如果是图片，添加 Base64 数据
    if file_type == 'image':
        response_dict = response.model_dump()
        response_dict['base64_data'] = processed.get('base64_data')
        return success_response(data=response_dict, message="文件上传成功")
    
    return success_response(data=response, message="文件上传成功")


@router.get("/list")
async def list_files(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取用户上传的文件列表"""
    statement = select(UploadedFile).where(
        UploadedFile.user_id == current_user.id,
        UploadedFile.is_deleted == False
    ).order_by(UploadedFile.created_at.desc())
    
    files = db.exec(statement).all()
    
    return success_response(data=[
        UploadedFileResponse(
            id=f.id,
            filename=f.filename,
            file_type=f.file_type,
            file_size=f.file_size,
            text_content=f.extracted_text[:200] + '...' if f.extracted_text and len(f.extracted_text) > 200 else f.extracted_text,
            created_at=f.created_at
        ) for f in files
    ])


@router.get("/{file_id}")
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """获取文件详情"""
    uploaded_file = db.get(UploadedFile, file_id)
    
    if not uploaded_file or uploaded_file.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 权限检查
    if uploaded_file.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此文件"
        )
    
    # 重新处理文件（获取最新内容）
    processed = FileService.process_file(uploaded_file.file_path, uploaded_file.file_type)
    
    response_dict = {
        'id': uploaded_file.id,
        'filename': uploaded_file.filename,
        'file_type': uploaded_file.file_type,
        'file_size': uploaded_file.file_size,
        'text_content': processed.get('text_content'),
        'created_at': uploaded_file.created_at
    }
    
    # 如果是图片，添加 Base64 数据
    if uploaded_file.file_type == 'image':
        response_dict['base64_data'] = processed.get('base64_data')
    
    return success_response(data=response_dict)


@router.delete("/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_session)
):
    """删除文件（软删除）"""
    uploaded_file = db.get(UploadedFile, file_id)
    
    if not uploaded_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 权限检查
    if uploaded_file.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此文件"
        )
    
    # 软删除
    uploaded_file.is_deleted = True
    db.add(uploaded_file)
    db.commit()
    
    # 可选：真实删除文件（注释掉以保留文件）
    # FileService.delete_file(uploaded_file.file_path)
    
    return success_response(message="文件删除成功")

