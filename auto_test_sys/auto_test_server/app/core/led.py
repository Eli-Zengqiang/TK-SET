#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2026/2/26
# @Author  : auto_test_sys
# @File    : led.py

import os


class LEDController:
    """LED控制器类，用于控制设备LED灯的颜色"""

    def __init__(self):
        # LED控制文件路径
        self.led_paths = {
            'green': '/sys/led/ledgall',   # 绿灯
            'red': '/sys/led/ledrall',     # 红灯
            'blue': '/sys/led/ledball'     # 蓝灯
        }

    def _write_led_value(self, led_type, value):
        """
        向LED控制文件写入值
        
        :param led_type: LED类型 ('green', 'red', 'blue')
        :param value: 控制值 (0-255)
        :return: 成功返回True，失败返回False
        """
        if led_type not in self.led_paths:
            print(f"未知的LED类型: {led_type}")
            return False

        if not 0 <= value <= 255:
            print(f"LED值必须在0-255范围内，当前值: {value}")
            return False

        try:
            with open(self.led_paths[led_type], 'w') as f:
                f.write(str(value))
            return True
        except Exception as e:
            print(f"控制{led_type}LED失败: {e}")
            return False

    def set_led_color(self, color):
        """
        设置LED颜色
        
        :param color: 颜色字符串 ('green', 'red', 'white', 'off')
                     green: 绿灯
                     red: 红灯
                     white: 白灯(红+绿+蓝)
                     off: 关闭所有灯
        :return: 成功返回True，失败返回False
        """
        # 先关闭所有LED
        self._write_led_value('green', 0)
        self._write_led_value('red', 0)
        self._write_led_value('blue', 0)

        if color == 'green':
            # 亮绿灯
            return self._write_led_value('green', 255)
        elif color == 'red':
            # 亮红灯
            return self._write_led_value('red', 255)
        elif color == 'white':
            # 亮白灯(红+绿+蓝)
            success = True
            success &= self._write_led_value('red', 255)
            success &= self._write_led_value('green', 255)
            success &= self._write_led_value('blue', 255)
            return success
        elif color == 'off':
            # 关闭所有灯(已在开头处理)
            return True
        else:
            print(f"不支持的颜色: {color}，支持的颜色: green, red, white, off")
            return False

    def set_custom_color(self, red_value=0, green_value=0, blue_value=0):
        """
        设置自定义LED颜色(RGB值)
        
        :param red_value: 红色值 (0-255)
        :param green_value: 绿色值 (0-255)
        :param blue_value: 蓝色值 (0-255)
        :return: 成功返回True，失败返回False
        """
        success = True
        success &= self._write_led_value('red', red_value)
        success &= self._write_led_value('green', green_value)
        success &= self._write_led_value('blue', blue_value)
        return success

# 测试代码
if __name__ == "__main__":
    import time
    
    # 创建LED控制器实例
    led = LEDController()
    
    print("测试LED控制功能...")
    
    # 测试绿灯
    print("亮绿灯...")
    led.set_led_color('green')
    time.sleep(2)
    
    # 测试红灯
    print("亮红灯...")
    led.set_led_color('red')
    time.sleep(2)
    
    # 测试白灯
    print("亮白灯...")
    led.set_led_color('white')
    time.sleep(2)
    
    # 测试关闭
    print("关闭所有灯...")
    led.set_led_color('off')
    time.sleep(1)
    
    # 测试自定义颜色
    print("测试自定义颜色...")
    led.set_custom_color(255, 128, 64)  # 橙色
    time.sleep(2)
    
    # 最终关闭
    led.set_led_color('off')
    print("LED测试完成")