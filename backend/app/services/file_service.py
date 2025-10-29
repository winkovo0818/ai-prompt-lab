"""文件处理服务"""
import os
import base64
import mimetypes
from typing import Optional, Tuple
from pathlib import Path
from datetime import datetime


class FileService:
    """文件处理服务"""
    
    # 上传目录
    UPLOAD_DIR = Path("uploads")
    
    # 支持的文件类型
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'],
        'text': ['.txt', '.md', '.csv', '.json', '.xml', '.html'],
        'document': ['.pdf', '.doc', '.docx'],
        'code': ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']
    }
    
    # 最大文件大小（10MB）
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @classmethod
    def init_upload_dir(cls):
        """初始化上传目录"""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        for subdir in ['images', 'documents', 'text', 'others']:
            (cls.UPLOAD_DIR / subdir).mkdir(exist_ok=True)
    
    @classmethod
    def get_file_type(cls, filename: str) -> str:
        """根据文件扩展名判断文件类型"""
        ext = Path(filename).suffix.lower()
        
        for file_type, extensions in cls.ALLOWED_EXTENSIONS.items():
            if ext in extensions:
                return file_type
        
        return 'other'
    
    @classmethod
    def is_allowed_file(cls, filename: str) -> bool:
        """检查文件是否允许上传"""
        ext = Path(filename).suffix.lower()
        
        all_extensions = []
        for extensions in cls.ALLOWED_EXTENSIONS.values():
            all_extensions.extend(extensions)
        
        return ext in all_extensions
    
    @classmethod
    def save_file(cls, file_content: bytes, filename: str, user_id: int) -> Tuple[str, str]:
        """
        保存文件到服务器
        
        Returns:
            (file_path, file_type): 文件路径和文件类型
        """
        cls.init_upload_dir()
        
        # 确定文件类型
        file_type = cls.get_file_type(filename)
        
        # 生成唯一文件名
        ext = Path(filename).suffix
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{user_id}_{timestamp}_{filename}"
        
        # 确定存储路径
        subdir = 'images' if file_type == 'image' else \
                 'documents' if file_type == 'document' else \
                 'text' if file_type == 'text' else 'others'
        
        file_path = cls.UPLOAD_DIR / subdir / unique_filename
        
        # 保存文件
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return str(file_path), file_type
    
    @classmethod
    def read_text_file(cls, file_path: str) -> Optional[str]:
        """读取文本文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    return f.read()
            except:
                return None
        except Exception as e:
            print(f"读取文件失败: {str(e)}")
            return None
    
    @classmethod
    def image_to_base64(cls, file_path: str) -> Optional[str]:
        """将图片转换为 Base64 编码"""
        try:
            with open(file_path, 'rb') as f:
                image_data = f.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                
                # 获取 MIME 类型
                mime_type, _ = mimetypes.guess_type(file_path)
                if not mime_type:
                    mime_type = 'image/jpeg'
                
                return f"data:{mime_type};base64,{base64_data}"
        except Exception as e:
            print(f"图片转 Base64 失败: {str(e)}")
            return None
    
    @classmethod
    def extract_pdf_text(cls, file_path: str) -> Optional[str]:
        """提取 PDF 文本（需要安装 PyPDF2）"""
        try:
            import PyPDF2
            
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text.strip()
        except ImportError:
            return "需要安装 PyPDF2: pip install PyPDF2"
        except Exception as e:
            print(f"PDF 文本提取失败: {str(e)}")
            return None
    
    @classmethod
    def process_file(cls, file_path: str, file_type: str) -> dict:
        """
        处理文件，提取内容
        
        Returns:
            包含文件信息的字典
        """
        result = {
            'file_path': file_path,
            'file_type': file_type,
            'text_content': None,
            'base64_data': None
        }
        
        if file_type == 'text' or file_type == 'code':
            # 读取文本内容
            result['text_content'] = cls.read_text_file(file_path)
        
        elif file_type == 'image':
            # 转换为 Base64
            result['base64_data'] = cls.image_to_base64(file_path)
        
        elif file_type == 'document':
            # 尝试提取文本
            if file_path.endswith('.pdf'):
                result['text_content'] = cls.extract_pdf_text(file_path)
        
        return result
    
    @classmethod
    def delete_file(cls, file_path: str) -> bool:
        """删除文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"删除文件失败: {str(e)}")
            return False

