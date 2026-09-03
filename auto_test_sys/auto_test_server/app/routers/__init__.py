from fastapi import APIRouter

from app.routers import test, files, system, devices

# Routers module init file
# 注意：设备控制路由同时注册在/devices和/hardware路径下，方便不同客户端调用
# Swagger路由用于提供本地化的API文档

# 创建API路由器
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(test.router, prefix="/test", tags=["测试"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])
api_router.include_router(system.router, prefix="/system", tags=["系统管理"])
api_router.include_router(devices.router, prefix="/devices", tags=["设备控制"])
#api_router.include_router(swagger.router, tags=["文档"])