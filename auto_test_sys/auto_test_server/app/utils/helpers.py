import hashlib
import secrets
import string
from typing import Any, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config.settings import settings

def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return hash_password(plain_password) == hashed_password

def create_access_token(data: Dict[str, Any], expires_delta: timedelta = None) -> str:
    """创建JWT访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_access_token(token: str) -> Dict[str, Any]:
    """验证JWT访问令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

def format_bytes(bytes_value: int) -> str:
    """格式化字节大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"

def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_allowed_file_extension(filename: str, allowed_extensions: list) -> bool:
    """检查文件扩展名是否被允许"""
    extension = get_file_extension(filename)
    return extension in [ext.lower() for ext in allowed_extensions]