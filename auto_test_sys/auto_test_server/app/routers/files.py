from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Form
from fastapi.responses import FileResponse
from typing import List, Optional

import shutil
from pathlib import Path
import hashlib


from app.utils.logger import app_logger
from config.settings import settings

router = APIRouter()

# 确保上传目录存在
UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

def validate_path(path: str) -> Path:
    """验证路径是否合法"""
    try:
        # 将相对路径转换为绝对路径
        full_path = (UPLOAD_DIR / path).resolve()
        # 检查路径是否在允许的目录内
        if not str(full_path).startswith(str(UPLOAD_DIR.resolve())):
            raise HTTPException(status_code=400, detail="Invalid path")
        return full_path
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid path")

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: Optional[str] = Form(None)
) -> dict:
    """上传文件到指定路径"""
    try:
        # 验证路径
        if path:
            target_dir = Path(path)
            if not target_dir.exists():
                target_dir.mkdir(parents=True, exist_ok=True)
        else:
            target_dir = UPLOAD_DIR

        # 检查文件大小
        file.file.seek(0, 2)  # 移动到文件末尾
        file_size = file.file.tell()
        file.file.seek(0)  # 回到文件开头

        if file_size > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE} bytes"
            )

        file_path = target_dir / file.filename

        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        app_logger.info(f"File uploaded: {file.filename} -> {file_path}")

        return {
            "success": True,
            "message": "File uploaded successfully",
            "data": {
                "filename": file.filename,
                "saved_path": str(file_path),
                "size": file_size
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{filename}")
async def download_file(filename: str, path: Optional[str] = Query(None)) -> FileResponse:
    """下载指定路径的文件"""
    try:
        # 验证路径
        if path:
            file_dir = Path(path)
        else:
            file_dir = UPLOAD_DIR

        file_path = file_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Download failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/md5/{filename}")
async def get_file_md5(filename: str, path: Optional[str] = Query(None)) -> dict:
    """获取指定文件的MD5码"""
    try:
        # 验证路径
        if path:
            file_dir = Path(path)
        else:
            file_dir = UPLOAD_DIR

        file_path = file_dir / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # 计算MD5码
        md5_hash = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)

        md5_code = md5_hash.hexdigest()

        app_logger.info(f"MD5 calculated for file: {filename} -> {md5_code}")

        return {
            "success": True,
            "message": "MD5 calculated successfully",
            "data": {
                "filename": filename,
                "md5": md5_code
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"MD5 calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

