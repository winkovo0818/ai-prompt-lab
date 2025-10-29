"""文件上传模型"""
from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class UploadedFile(SQLModel, table=True):
    """上传的文件表"""
    __tablename__ = "uploaded_files"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    filename: str = Field(max_length=255)  # 原始文件名
    file_path: str = Field(max_length=500)  # 服务器存储路径
    file_type: str = Field(max_length=50)  # 文件类型（image, text, pdf, etc.）
    mime_type: str = Field(max_length=100)  # MIME 类型
    file_size: int  # 文件大小（字节）
    extracted_text: Optional[str] = Field(default=None)  # 提取的文本内容
    is_deleted: bool = Field(default=False)  # 软删除标记
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UploadedFileResponse(SQLModel):
    """文件上传响应"""
    id: int
    filename: str
    file_type: str
    file_size: int
    preview_url: Optional[str] = None  # 预览 URL
    text_content: Optional[str] = None  # 文本内容（用于文本文件）
    created_at: datetime

