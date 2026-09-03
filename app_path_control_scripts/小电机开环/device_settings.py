from Motor import Motor
from lidar_http import  set_ptp,set_return_mode
from minMotor import MinMotor


import os
import time

def power_model():
    '''
    给需要配置的模块上电
    :return:
    '''
    # 开启雷达
    with open('/proc/rp_power/radar', 'w') as f:
        f.write('1')
    # 开启小电机
    with open('/proc/rp_power/motor', 'w') as f:
        f.write('1')
    # 开启转台
    with open('/proc/rp_power/zt', 'w') as f:
        f.write('1')



def lidar_setting():
    '''
    检查IP，配置PTP和回波模式
    :return:
    '''
    print("----------------------1.检查雷达连接，需先确保雷达已上电")
    if os.system('ping -c 1 -w 1 192.168.1.201')==0:
        print("\033[92m%s\033[0m" % "----------------------雷达网络正常")
    else:
        print("\033[91m%s\033[0m" % "----------------------雷达网络错误")
        return False
    print("----------------------2.设置雷达PTP授时")
    if set_ptp():
        print("\033[92m%s\033[0m" % "----------------------雷达PTP授时设置成功")
    else:
        print("\033[91m%s\033[0m" % "----------------------雷达PTP授时设置失败")
    print("----------------------3.设置雷达回波模式")
    if set_return_mode():
        print("\033[92m%s\033[0m" % "----------------------雷达PTP回波模式设置成功")
    else:
        print("\033[91m%s\033[0m" % "----------------------雷达PTP回波模式设置失败")

def motor_setting():
    '''
    转台设置，电流、最大速度、加减速度、帧率
    :return:
    '''
    try:
        mo=Motor()
        mo.cmd_set_max_speed(25.0)
        print("设置最大速度25")
        time.sleep(1)
        mo.cmd_set_current(10)
        print("设置运动电流10")
        mo.cmd_set_stop_current(0.0)
        print("设置静止电流0")
        time.sleep(1)
        mo.cmd_set_max_addacc(20)
        print("设置最大加速度")
        time.sleep(1)
        mo.cmd_set_max_racc(20)
        print("设置最大减速度")
        time.sleep(1)
        mo.cmd_set_ratio()
        print("设置数据帧率")
        time.sleep(1)
        mo.cmd_save_para()
        print("保存所有参数")
        time.sleep(1)
    except Exception as e:
        print(e)


def min_motor_setting():
    '''
    设置小电机细分
    :return:
    '''
    try:
        mo=MinMotor()
        mo.cmd_set_xf(128)
        print("设置电机细分为128")
        mo.cmd_set_open()
        print("设置电机为开环控制")
    except Exception as e:
        print(e)

def camera_json_setting(delay_time=10):
    '''
    配置相机ID
    :return:
    '''
    start_time = time.time()
    while True:
        out = os.popen('lsusb')
        lines = out.readlines()
        print(lines)
        sony_count = 0
        for line in lines:
            if 'Sony' in line:
                sony_count += 1
        if sony_count >= 2:
            print(f"获取2个相机成功耗费时间：{time.time() - start_time}")
            break
        current_time = time.time()
        if current_time - start_time >= delay_time:
            print(f"【错误】！！！！！！！超过delay_time:{delay_time}，运行脚本前需要保证两个相机是开启的！")
            break

if __name__ == "__main__":
    print("各模块上电...")
    power_model()
    print("等待雷达启动完毕，大概需要30S...")
    time.sleep(40)
    print("设置雷达中...")
    lidar_setting()
    time.sleep(3)
    print("设置转台中...")
    motor_setting()
    time.sleep(3)
    print("设置小电机中...")
    min_motor_setting()


