#!/usr/bin/env python3
import platform
import os
import datetime

print("=== 系统信息 ===")
print(f"操作系统: {platform.system()} {platform.release()}")
print(f"系统版本: {platform.version()}")
print(f"计算机名: {platform.node()}")
print(f"处理器: {platform.processor()}")
print(f"Python版本: {platform.python_version()}")
print(f"当前用户: {os.getlogin()}")
print(f"当前时间: {datetime.datetime.now()}")
print("=" * 20)
