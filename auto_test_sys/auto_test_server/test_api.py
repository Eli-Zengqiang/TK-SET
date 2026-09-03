#!/usr/bin/env python3
"""
API测试脚本
测试新增的设备控制API端点
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_endpoint(endpoint, method="GET", data=None, expected_status=200):
    """测试单个API端点"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"accept": "application/json"}
    
    if data:
        headers["Content-Type"] = "application/json"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=5)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=5)
        else:
            print(f"❌ 不支持的方法: {method}")
            return False
            
        if response.status_code == expected_status:
            result = response.json()
            if result.get("success", False):
                print(f"✅ {method} {endpoint} - 成功")
                print(f"   消息: {result.get('message', 'N/A')}")
                return True
            else:
                print(f"⚠️  {method} {endpoint} - API返回失败")
                print(f"   错误: {result.get('message', 'N/A')}")
                return False
        else:
            print(f"❌ {method} {endpoint} - 状态码错误: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"⏰ {method} {endpoint} - 请求超时")
        return False
    except requests.exceptions.ConnectionError:
        print(f"🔌 {method} {endpoint} - 连接错误")
        return False
    except Exception as e:
        print(f"💥 {method} {endpoint} - 异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始API端点测试...\n")
    
    # 测试基础端点
    test_cases = [
        # 基础测试端点
        ("/test/ping", "GET"),
        ("/test/status", "GET"),
        
        # 设备状态查询
        ("/devices/status", "GET"),
        
        # 电源管理API
        ("/devices/power/status/radar", "GET"),
        ("/devices/power/status/motor", "GET"),
        
        # 转台电机API（需要硬件连接，预期会失败）
        ("/devices/motor/configure", "POST", {}),
        
        # 小电机API（需要硬件连接，预期会失败）
        ("/devices/min-motor/configure", "POST", {}),
        
        # 雷达API（需要网络连接，预期会失败）
        ("/devices/lidar/sn", "GET"),
        
        # 倾角仪API（需要硬件连接，预期会失败）
        ("/devices/inclinometer/read", "GET"),
        
        # 系统配置API
        ("/devices/config/wifi-setup", "POST", {}),
        ("/devices/config/time-sync", "POST", {"target_time": "2026-01-01 12:00:00"}),
        
        # 批量操作API
        ("/devices/setup/all-devices", "POST", {}),
    ]
    
    passed = 0
    failed = 0
    
    for case in test_cases:
        endpoint, method = case[0], case[1]
        data = case[2] if len(case) > 2 else None
        
        if test_endpoint(endpoint, method, data):
            passed += 1
        else:
            failed += 1
        
        time.sleep(0.1)  # 避免请求过于频繁
    
    print(f"\n📊 测试结果统计:")
    print(f"   ✅ 通过: {passed}")
    print(f"   ❌ 失败: {failed}")
    print(f"   📈 通过率: {passed/(passed+failed)*100:.1f}%")
    
    if failed > 0:
        print(f"\n💡 提示: 部分API失败是正常的，因为:")
        print(f"   • 硬件设备未连接")
        print(f"   • 网络设备不可达")
        print(f"   • 需要特定的运行环境")
    
    print(f"\n🎯 API文档地址: http://127.0.0.1:8000/docs")
    print(f"   可以在这里查看完整的API文档和在线测试")

if __name__ == "__main__":
    main()