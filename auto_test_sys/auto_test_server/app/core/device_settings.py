from .Motor import Motor
from .lidar_http import  set_ptp,set_return_mode
from .minMotor import MinMotor


import os
import time

#目前新相机设备只有雷达、转台、小电机需要配置。


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
        mo.cmd_set_work_mode()
        print("设置电机为开环控制")
        mo.cmd_set_open_current(1000, True)
        print("设置电机为开环电流")
    except Exception as e:
        print(e)






