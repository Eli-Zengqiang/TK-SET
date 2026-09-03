#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试按钮禁用功能的验证脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from src.utils.config_manager import ConfigManager
from src.api.client import APIClient
from src.ui.individual_control_tab import IndividualControlTab
from src.ui.integrated_test_tab import IntegratedTestTab

def test_individual_control_buttons():
    """测试单模块控制标签页的按钮禁用功能"""
    print("=== 测试单模块控制标签页按钮禁用功能 ===")
    
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    api_client = APIClient(config_manager.get_server_url())
    
    # 创建单模块控制标签页
    tab = IndividualControlTab(api_client, config_manager)
    
    # 测试按钮禁用功能
    print("测试电源管理按钮...")
    
    # 模拟点击电源上电按钮
    print(f"电源上电按钮初始状态: {tab.power_on_btn.isEnabled()}")
    tab.power_on_module()  # 这会触发execute_api_call
    
    # 等待一小段时间让线程启动
    QTimer.singleShot(100, lambda: print(f"电源上电按钮执行后状态: {tab.power_on_btn.isEnabled()}"))
    
    # 测试其他按钮组
    print("\n测试电机控制按钮...")
    print(f"找零位按钮初始状态: {tab.find_zero_btn.isEnabled()}")
    tab.motor_find_zero()
    QTimer.singleShot(100, lambda: print(f"找零位按钮执行后状态: {tab.find_zero_btn.isEnabled()}"))
    
    print("\n测试完成")
    return True

def test_integrated_test_buttons():
    """测试集成测试标签页的按钮禁用功能"""
    print("=== 测试集成测试标签页按钮禁用功能 ===")
    
    app = QApplication(sys.argv)
    config_manager = ConfigManager()
    api_client = APIClient(config_manager.get_server_url())
    
    # 创建集成测试标签页
    tab = IntegratedTestTab(api_client, config_manager)
    
    # 测试按钮状态
    print("测试集成测试按钮初始状态...")
    print(f"开始测试按钮: {tab.start_test_btn.isEnabled()}")
    print(f"停止测试按钮: {tab.stop_test_btn.isEnabled()}")
    print(f"生成报告按钮: {tab.generate_report_btn.isEnabled()}")
    
    # 模拟选择模块
    tab.module_selector.select_all()
    
    # 模拟点击开始测试
    print("\n模拟点击开始测试...")
    tab.start_integrated_test()
    
    # 检查按钮状态变化
    print(f"开始测试按钮(执行后): {tab.start_test_btn.isEnabled()}")
    print(f"停止测试按钮(执行后): {tab.stop_test_btn.isEnabled()}")
    
    return True

def main():
    """主测试函数"""
    print("开始测试按钮禁用功能...")
    
    try:
        # 测试单模块控制
        test_individual_control_buttons()
        
        print("\n" + "="*50 + "\n")
        
        # 测试集成测试
        test_integrated_test_buttons()
        
        print("\n所有测试完成!")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)