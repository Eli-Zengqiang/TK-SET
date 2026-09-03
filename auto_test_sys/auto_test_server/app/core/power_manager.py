# PowerManager.py

import os
import time

class PowerManager:
    def __init__(self):
        self.power_paths = {
            'camera1':'/sys/control/power_camera1',
            'camera2': '/sys/control/power_camera2',
            'radar': '/proc/rp_power/radar',
            'zt':'/proc/rp_power/zt',
            'motor': '/proc/rp_power/motor',
            'laser':'/proc/rp_power/laser',
            'inc':'/proc/rp_power/angle',
            'led':'/proc/rp_power/power-led'
        }

    def power_on(self, module):
        """
        给指定模块上电
        :param module: 模块名称 ('radar', 'motor', 'zt')
        :return: 成功返回True，失败返回False
        """
        if module not in self.power_paths:
            print(f"未知模块: {module}")
            return False

        try:
            with open(self.power_paths[module], 'w') as f:
                f.write('1')
            if module == 'camera1':#相机需要额外打开usb
                with open('/sys/control/camera_power1', 'w') as f:
                    f.write('1')
            elif module == 'camera2':
                with open('/sys/control/camera_power2', 'w') as f:
                    f.write('1')

            print(f"{module} 上电成功")
            return True
        except Exception as e:
            print(f"{module} 上电失败: {e}")
            return False

    def power_off(self, module):
        """
        给指定模块断电
        :param module: 模块名称 ('radar', 'motor', 'zt')
        :return: 成功返回True，失败返回False
        """
        if module not in self.power_paths:
            print(f"未知模块: {module}")
            return False

        try:
            with open(self.power_paths[module], 'w') as f:
                f.write('0')
            print(f"{module} 断电成功")
            return True
        except Exception as e:
            print(f"{module} 断电失败: {e}")
            return False

    def check_power_status(self, module):
        """
        检查指定模块的上电状态
        :param module: 模块名称 ('radar', 'motor', 'zt')
        :return: 上电返回True，断电返回False
        """
        if module not in self.power_paths:
            print(f"未知模块: {module}")
            return False

        try:
            with open(self.power_paths[module], 'r') as f:
                status = f.read().strip()
            if status == '1':
                print(f"{module} 当前状态: 上电")
                return True
            else:
                print(f"{module} 当前状态: 断电")
                return False
        except Exception as e:
            print(f"无法读取 {module} 状态: {e}")
            return False

    def power_on_all(self):
        """
        给所有模块上电
        """
        for module in self.power_paths.keys():
            self.power_on(module)
            time.sleep(1)  # 等待一段时间再给下一个模块上电

    def power_off_all(self):
        """
        给所有模块断电
        """
        for module in self.power_paths.keys():
            self.power_off(module)
            time.sleep(1)  # 等待一段时间再给下一个模块断电

if __name__ == "__main__":
    pm = PowerManager()

    # 示例：给所有模块上电
    pm.power_on_all()

    # 示例：检查雷达模块状态
    pm.check_power_status('radar')

    # 示例：给电机模块断电
    pm.power_off('motor')
