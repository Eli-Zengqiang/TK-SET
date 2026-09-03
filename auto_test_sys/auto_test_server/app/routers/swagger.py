from fastapi import APIRouter, Request
from fastapi.openapi.docs import get_swagger_ui_html

router = APIRouter()

@router.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    """自定义Swagger UI页面，使用本地资源"""
    openapi_url = request.app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API文档 - Swagger UI",
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui/favicon-32x32.png"
    )

@router.get("/redoc", include_in_schema=False)
async def custom_redoc_html(request: Request):
    """自定义ReDoc页面"""
    openapi_url = request.app.openapi_url
    return get_swagger_ui_html(
        openapi_url=openapi_url,
        title="API文档 - ReDoc",
        swagger_js_url="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js",
        swagger_css_url="",  # ReDoc使用内联样式
        swagger_favicon_url=""
    )