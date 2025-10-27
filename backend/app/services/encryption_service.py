"""加密服务 - API密钥加密存储"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from typing import Optional


class EncryptionService:
    """加密服务 - 用于加密存储敏感信息如API密钥"""
    
    # 从环境变量或配置文件获取主密钥
    # 注意：实际部署时应该从安全的配置管理系统获取
    _MASTER_KEY = os.getenv('ENCRYPTION_MASTER_KEY', 'default-master-key-change-in-production')
    _SALT = os.getenv('ENCRYPTION_SALT', 'default-salt-change-in-production').encode()
    
    _cipher = None
    
    @classmethod
    def _get_cipher(cls) -> Fernet:
        """获取或创建加密器"""
        if cls._cipher is None:
            # 使用PBKDF2HMAC从主密钥派生加密密钥
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=cls._SALT,
                iterations=100000,
                backend=default_backend()
            )
            key = base64.urlsafe_b64encode(kdf.derive(cls._MASTER_KEY.encode()))
            cls._cipher = Fernet(key)
        
        return cls._cipher
    
    @staticmethod
    def encrypt_api_key(api_key: str) -> str:
        """
        加密API密钥
        
        Args:
            api_key: 明文API密钥
        
        Returns:
            加密后的密钥（Base64编码的字符串）
        """
        if not api_key:
            return ""
        
        try:
            cipher = EncryptionService._get_cipher()
            encrypted = cipher.encrypt(api_key.encode())
            return encrypted.decode()
        except Exception as e:
            print(f"加密失败: {str(e)}")
            raise ValueError("API密钥加密失败")
    
    @staticmethod
    def decrypt_api_key(encrypted_key: str) -> str:
        """
        解密API密钥
        
        Args:
            encrypted_key: 加密的密钥
        
        Returns:
            明文API密钥
        """
        if not encrypted_key:
            return ""
        
        try:
            cipher = EncryptionService._get_cipher()
            decrypted = cipher.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            print(f"解密失败: {str(e)}")
            raise ValueError("API密钥解密失败")
    
    @staticmethod
    def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
        """
        遮蔽API密钥（用于显示）
        
        Args:
            api_key: API密钥
            visible_chars: 保留可见的字符数
        
        Returns:
            遮蔽后的密钥，如 "sk-...abcd"
        """
        if not api_key:
            return ""
        
        if len(api_key) <= visible_chars:
            return '*' * len(api_key)
        
        # 尝试识别OpenAI风格的key（sk-xxx）
        if api_key.startswith('sk-') or api_key.startswith('Bearer '):
            prefix = api_key.split('-')[0] + '-' if '-' in api_key else ''
            return f"{prefix}...{api_key[-visible_chars:]}"
        
        return f"...{api_key[-visible_chars:]}"
    
    @staticmethod
    def generate_salt() -> str:
        """生成随机盐值"""
        return base64.urlsafe_b64encode(os.urandom(16)).decode()
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        哈希密码（使用PBKDF2HMAC）
        
        Returns:
            (hashed_password, salt)
        """
        if salt is None:
            salt = EncryptionService.generate_salt()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
            backend=default_backend()
        )
        
        hashed = base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()
        
        return hashed, salt
    
    @staticmethod
    def verify_password(password: str, hashed_password: str, salt: str) -> bool:
        """验证密码"""
        try:
            computed_hash, _ = EncryptionService.hash_password(password, salt)
            return computed_hash == hashed_password
        except Exception:
            return False
    
    @staticmethod
    def encrypt_sensitive_data(data: str) -> str:
        """加密敏感数据（通用方法）"""
        return EncryptionService.encrypt_api_key(data)
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str) -> str:
        """解密敏感数据（通用方法）"""
        return EncryptionService.decrypt_api_key(encrypted_data)


# 使用示例
if __name__ == "__main__":
    # 测试加密
    api_key = "sk-1234567890abcdefghijklmnop"
    
    print(f"原始密钥: {api_key}")
    
    # 加密
    encrypted = EncryptionService.encrypt_api_key(api_key)
    print(f"加密后: {encrypted}")
    
    # 解密
    decrypted = EncryptionService.decrypt_api_key(encrypted)
    print(f"解密后: {decrypted}")
    
    # 遮蔽显示
    masked = EncryptionService.mask_api_key(api_key)
    print(f"遮蔽显示: {masked}")
    
    print(f"\n验证: {api_key == decrypted}")

