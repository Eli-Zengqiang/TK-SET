#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/8 15:38
# @Author  : bhb
# @Email   : 
# @File    : mainThread.py

import sys, getopt
import time
import subprocess

from Inclinometer import Inclinometer
from Lidar_XT import Lidar_XT
from Motor import Motor


def test_pcas(project_name="t1"):
    '''
    采集点云数据
    :return:
    '''

    mo=Motor()

    print("转台找零...")
    mo.cmd_find_zero()
    print("转台回到零位")
    mo.cmd_set_position(0)

    print("1.获取倾角仪数据...")
    inc=Inclinometer()
    inc.save_inc(project_name+"_inc.txt")

    print("2.转台开始旋转")
    xt = Lidar_XT()
    mo.cmd_set_index()
    mo.start_read()
    xt.start_read()

    mo.cmd_set_speed(2.97)
    time.sleep(65)
    mo.cmd_stop_all()

    mo.stop_read()
    xt.stop_read()

    mo.start_write(project_name + "_angles.txt")
    xt.start_write(project_name + "_lidar.bin")

    mo.stop_write()
    xt.stop_write()
    #mo.cmd_set_position(0)


def test_picts(project_name="t1",angle_step=30):
    #angles=[0,45,90,135,180,225,270,315]#需要拍照的角度
    angles=[i for i in range(0,360,angle_step)]
    print(angles)

    commond = "./RemoteCli"#把相机程序启动
    process = subprocess.Popen((commond), shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(5)
    mo = Motor()
    print("1.1.转台找零...")
    mo.cmd_find_zero()
    angles_str_list=[]
    for target_angle in angles:
        print("当前设置角度：",target_angle)
        mo.cmd_set_position(target_angle)
        time.sleep(1)
        #mo.cmd_find_zero()
        angles_str_list.append(str(mo.angle)+"\n")
        with open("/app/sony/build/pict_func", "w") as f:  # 触发相机程序
            f.write("1")
        time.sleep(3)

    with open("/app/sony/build/pict_func","w") as f:#关闭相机程序
        f.write("2")
    print("照片采集完成，等待退出")
    with open(f"{project_name}_p_angle.txt","w") as f:#关闭相机程序
        f.writelines(angles_str_list)
    time.sleep(10)


def test_light(start_ms,end_ms):
    '''
    测试闪光灯
    :param start_ms:
    :param end_ms:
    :return:
    '''
    for i in range(start_ms,end_ms):
        with open("/app/CrSDK/build/pict_func", "w") as f:  # 触发相机程序
            f.write(str(i))
        time.sleep(5)


if __name__ == "__main__":
    projectfile = ""
    angle=30
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:p:a:", ["pfile="])
    except getopt.GetoptError:
        print(' -p <projectfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-p <projectfile>')
            sys.exit()
        elif opt in ("-p", "--pfile"):
            test_pcas(arg)
        elif opt == '-c':
            test_picts(arg,angle)
        elif opt == '-a':
            angle=int(arg)
    # if projectfile != "":
    #     test_pcas(projectfile)


