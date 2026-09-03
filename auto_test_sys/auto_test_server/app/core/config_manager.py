import subprocess
from .lidar_http import get_sn
from datetime import datetime


def configure_wifi_ssid():
    """
    配置 WiFi 的 SSID 名称。
    1. 使用 get_sn 获取 SN 码。
    2. 修改 /etc/hostapd.conf 文件中的 ssid 字段。
    3. 重启 hostapd 服务以应用更改。
    """
    try:
        # 获取 SN 码
        sn = get_sn()
        if not sn:
            return False,"无法获取 SN 码"

        # 提取 SN 码的后 6 位
        sn_suffix = sn[-6:]

        # 构造新的 SSID
        new_ssid = f"TK-SMARTEYE-V2-{sn_suffix}"

        # 读取并修改 hostapd 配置文件
        config_file_path = "/etc/hostapd.conf"
        with open(config_file_path, "r") as file:
            lines = file.readlines()

        # 更新 ssid 行
        updated_lines = []
        for line in lines:
            if line.startswith("ssid="):
                updated_lines.append(f"ssid={new_ssid}\n")
            else:
                updated_lines.append(line)

        # 写回配置文件
        with open(config_file_path, "w") as file:
            file.writelines(updated_lines)

        # 重启 hostapd 服务
        #subprocess.run(["systemctl", "restart", "hostapd"], check=True)

        print(f"WiFi SSID 已成功更新为: {new_ssid}")
        return True,"WiFi SSID 已成功更新为: " + new_ssid
    except Exception as e:
        print(f"配置 WiFi SSID 失败: {e}")
        return False,str(e)

def update_system_time(target_time):
    """
    更新系统时间和硬件时钟。

    参数:
        target_time (str): 目标时间，格式为 "YYYY-MM-DD HH:MM:SS"

    返回:
        tuple: (bool, str)
               第一个元素表示是否成功，
               第二个元素是结果描述或错误信息。
    """
    try:
        # 验证时间格式
        datetime.strptime(target_time, "%Y-%m-%d %H:%M:%S")

        # 设置系统时间
        subprocess.run(["date", "-s", target_time], check=True)

        # 将系统时间写入硬件时钟
        subprocess.run(["hwclock", "-w"], check=True)

        # 读取硬件时钟时间验证
        result = subprocess.run(["hwclock", "-r"], capture_output=True, text=True, check=True)
        hw_time = result.stdout.strip()

        print(f"系统时间已更新为: {target_time}")
        print(f"硬件时钟时间: {hw_time}")
        return True, f"系统时间已更新为: {target_time}, 硬件时钟时间: {hw_time}"
    except subprocess.CalledProcessError as e:
        error_msg = f"执行命令失败: {e}"
        print(error_msg)
        return False, error_msg
    except ValueError as e:
        error_msg = f"时间格式错误: {e}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"未知错误: {e}"
        print(error_msg)
        return False, error_msg
