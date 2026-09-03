#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/11/15 16:30
# @Author  : bhb
# @Email   : 
# @File    : test_light.py
import time

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

    with open("/app/CrSDK/build/pict_func", "w") as f:  # 关闭相机程序
        f.write("1")

def delayMsecond(t):
    start,end = 0,0
    start = time.time() * pow(10,7)     #精确至ns级别
    while(end - start < t* pow(10,3)):
        end = time.time() * pow(10,7)

def test_light_hard(start_ms,end_ms,step=1):
    '''
    测试闪光灯
    :param start_ms:
    :param end_ms:
    :return:
    '''
    for i in range(start_ms,end_ms,step):
        with open("/sys/control/camera_on1", "w") as f:  # 触发相机拍照
            f.write("1")
        start=time.time()
        #delayMsecond(i)
        time.sleep(i/1000)
        print("当前延迟：",time.time()-start)
        with open("/sys/control/light_on", "w") as f:  # 触发闪光灯
            f.write("1")
        time.sleep(3)