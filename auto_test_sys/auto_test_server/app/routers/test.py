from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
from app.utils.logger import app_logger

router = APIRouter()

@router.get("/ping")
async def ping() -> Dict[str, str]:
    """测试连接"""
    return {"message": "pong", "timestamp": str(time.time())}

@router.post("/echo")
async def echo(data: Dict[str, Any]) -> Dict[str, Any]:
    """回显测试"""
    app_logger.info(f"Echo request received: {data}")
    return {"received": data, "timestamp": time.time()}

@router.get("/status")
async def get_status() -> Dict[str, Any]:
    """获取服务状态"""
    return {
        "status": "running",
        "uptime": "service is running normally",
        "timestamp": time.time()
    }