#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/10/23 10:10
# @Author  : bhb
# @Email   : 
# @File    : minMotor.py


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 16:45
# @Author  : bhb
# @Email   :
# @File    : Motor.py

import sys, getopt
import serial
import time
import struct
import threading
import math
import io


class MinMotor:

    def __init__(self,com_name="/dev/ttyS7",bound_raito=38400):
        self.com = serial.Serial(com_name, bound_raito)
        self.speed=0.0#当前速度
        self.angle=0.0#当前角度

        self.packets_buffer = []
        self.data_num = 0
        self.set_index_time=0

    def __del__(self):
        if self.com.is_open:
            self.com.close()




    def cmd_set_zero(self,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01,0x0a,0x6d,0x6b])  # 设置零位
        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)

            if len(data)>1:
                print(data)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break

    def cmd_set_en(self,state=0,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01,0xf3,state,0x6b])  # 设置使能 0，1
        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)>1:
                print(data)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break

    def cmd_read_en(self,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01,0x3a,0x6b])  # 设置使能 0，1
        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)>1:
                print(data)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break

    def cmd_read_zero_state(self,delay_time=60):
        '''
        读取单圈上电回零状态
        :param delay_time:
        :return:
        '''
        self.com.flushInput()
        self.com.write([0x01,0x3f,0x6b])  # 设置使能 0，1
        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)>1:
                print(data)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break

    def cmd_read_angle(self,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01,0x30,0x6b])
        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)==4 and data[0]==0x01 and data[3]==0x6b:
                print(data[1],data[2])
                angle = struct.unpack('>H', data[1:3])[0]#data[1]*(2<<8)+data[2]
                print(angle)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break



if __name__ == "__main__":
    mo=MinMotor()
    mo.cmd_read_angle()



