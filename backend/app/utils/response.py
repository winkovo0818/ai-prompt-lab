from typing import Any, Optional
from pydantic import BaseModel


class APIResponse(BaseModel):
    """统一API响应格式"""
    code: int
    data: Any = None
    message: str = "success"


def success_response(data: Any = None, message: str = "success") -> dict:
    """成功响应"""
    return {
        "code": 0,
        "data": data,
        "message": message
    }


def error_response(code: int = -1, message: str = "error", data: Any = None) -> dict:
    """错误响应"""
    return {
        "code": code,
        "data": data,
        "message": message
    }

