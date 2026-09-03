#!/usr/bin/env python3
"""
Auto Test Server 启动脚本
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.main import app
import uvicorn
from config.settings import settings

def main():
    """主函数"""
    print(f"🚀 Starting {settings.PROJECT_NAME}...")
    print(f"📝 Version: {settings.VERSION}")
    print(f"🌐 Host: {settings.HOST}:{settings.PORT}")
    print(f"📄 Docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()