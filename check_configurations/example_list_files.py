#!/usr/bin/env python3
import os
import sys

path = "." if len(sys.argv) < 2 else sys.argv[1]
print(f"=== 目录内容: {os.path.abspath(path)} ===")

try:
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            print(f"文件: {item} ({size} 字节)")
        elif os.path.isdir(item_path):
            print(f"目录: {item}/")
    print("=" * 40)
except Exception as e:
    print(f"错误: {e}")
