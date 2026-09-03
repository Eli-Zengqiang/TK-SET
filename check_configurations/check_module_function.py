#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/10 16:45
# @Author  : bhb
# @Email   : 
# @File    : Motor.py
import os
import sys, getopt
import serial
import time
from datetime import datetime
import struct
import threading
import math
import io
import requests
import subprocess
#from smart_eye2_1.app_path_control_scripts.Motor import Motor
#from smart_eye2_1.app_path_control_scripts.lidar_http import  set_ptp,set_return_mode
#from smart_eye2_1.app_path_control_scripts.minMotor import MinMotor

class Motor:

    def __init__(self,com_name="/dev/ttyS1",bound_raito=512000):  #self,com_name="/dev/ttyS1",bound_raito=512000
        self.com = serial.Serial(com_name, bound_raito)
        #com = serial.Serial("/dev/ttyS1", 512000)
        self.speed=0.0#当前速度
        self.angle=0.0#当前角度
        self.id=0#帧序号
        self.packets_buffer = []
        self.data_num = 0
        self.set_index_time=0

    def __del__(self):
        if self.com.is_open:
            self.com.close()

    def debug(self):
        self.com.flushInput()
        self.com.write([0xEB,0x20,0x00,0x00,0xA0,0x41,0x00,0x00,0xEC,0xBE])  # 寻找零位
        pass

    def _decode_state(self,code):
        '''
        解析状态
        :param code:
        :return:
        '''
        print(code)
        if ((code & 0b1) > 0):
            print("转台已过零")
        else:
            print("转台未过零")

        if ((code & 0b10) > 0):
            print("转台速度为零")
        else:
            print("转台速度不为零")

        if ((code & 0b100) > 0):
            print("转台到达目标速度")
        else:
            print("转台未到达目标速度")

        if ((code & 0b1000) > 0):
            print("转台到达目标位置")
        else:
            print("转台未到达目标位置")

        if ((code & 0b10000) > 0):
            print("供电电压异常")
        else:
            print("供电电压正常")

    def cmd_find_zero(self,delay_time=60):
        self.com.flushInput()
        self.com.write([235, 48, 0, 0, 0, 0, 0, 0, 27, 190])  # 寻找零位
        is_over_zero=False
        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            for i in range(len(data)):
                if data[i] == 0x55 and i + 15 < len(data) and data[i + 15] == 0xAA:
                    self.speed = struct.unpack('<f', data[i + 4:i + 8])[0]
                    self.angle = struct.unpack('<f', data[i + 8:i + 12])[0]
                    self.id = struct.unpack('<H', data[i + 12:i + 14])[0]
                    print("当前角度", self.angle)
                    if ((data[i+2] & 0b1)>0):
                        is_over_zero=True
                        self._decode_state(data[i+2])
                        break
            if is_over_zero:
                print("云台已过零")
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出找零")
                break
        self.cmd_stop_all()
        if is_over_zero:
            return True
        return False

    def cmd_stop_all(self):
        self.com.write([235, 0, 0, 0, 0, 0, 0, 0, 235, 190])  # 停止所有操作
        time.sleep(0.5)

    def cmd_set_speed(self,set_speed=5.0):
        '''
        速度控制
        :param set_speed:
        :return:
        '''
        send_cmd_bytes = [235, 2, 0, 0, 160, 64, 0, 0, 205, 190]
        send_cmd_bytes[2:6] = struct.pack('<f', set_speed)
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        self.com.write(send_cmd_bytes)  # 5速度控制

    def cmd_set_max_speed(self,set_speed=20.0):
        '''
        速度控制
        :param set_speed:
        :return:
        '''
        send_cmd_bytes = [0xEB, 0x22, 0, 0, 0, 0, 0, 0, 205, 0xBE]
        send_cmd_bytes[2:6] = struct.pack('<f', set_speed)
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        self.com.write(send_cmd_bytes)  # 5速度控制

    def cmd_set_max_addacc(self,set_speed=20.0):
        '''
        加速度控制
        :param set_speed:
        :return:
        '''
        send_cmd_bytes = [235, 32, 0, 0, 160, 64, 0, 0, 205, 190]
        send_cmd_bytes[2:6] = struct.pack('<f', set_speed)
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        self.com.write(send_cmd_bytes)  # 5速度控制
        print(send_cmd_bytes)

    def cmd_set_current(self,set_current=8.0):
        '''
        设置运动电流
        :param set_current:
        :return:
        '''
        send_cmd_bytes = [235, 16, 0, 0, 0, 0, 0, 0, 0, 190]
        send_cmd_bytes[2:6] = struct.pack('<f', set_current)
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        self.com.write(send_cmd_bytes)  # 5速度控制

    def cmd_set_stop_current(self,set_current=0.0):
        '''
        设置静止电流
        :param set_current:
        :return:
        '''
        send_cmd_bytes = [235, 17, 0, 0, 0, 0, 0, 0, 0, 190]
        send_cmd_bytes[2:6] = struct.pack('<f', set_current)
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        self.com.write(send_cmd_bytes)

    def cmd_set_max_racc(self,set_speed=20.0):
        '''
        减速度控制
        :param set_speed:
        :return:
        '''
        send_cmd_bytes = [235, 33, 0, 0, 160, 64, 0, 0, 205, 190]
        send_cmd_bytes[2:6] = struct.pack('<f', set_speed)
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        print(send_cmd_bytes)
        self.com.write(send_cmd_bytes)  # 5速度控制

    def cmd_set_ratio(self,set_ratio=1000):
        '''
        设置帧率
        :param set_ratio:
        :return:
        '''
        send_cmd_bytes = [0xEB, 0x34, 0, 0, 0, 0, 0, 0, 0, 0xBE]
        send_cmd_bytes[2:6] = struct.pack('<f', set_ratio)
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        self.com.write(send_cmd_bytes)

    def cmd_set_index(self):
        '''
        设置帧序号
        :param set_index:0
        :return:
        '''
        send_cmd_bytes = [235, 53, 0, 0, 0, 0, 0, 0, 32, 190]

        self.com.flushInput()
        self.com.write(send_cmd_bytes)
        self.set_index_time=time.time()
        print(self.set_index_time)
        is_finding_id=True
        current_recv_time=0
        while is_finding_id:
            # 需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)

            if len(data) > 0:
                current_recv_time = time.time()
                print(f"--------------------数据长度：{len(data)},收到的时间：{current_recv_time}")
                for i in range(len(data)):
                    if data[i] == 0x55 and i + 15 < len(data) and data[i + 15] == 0xAA:
                        sum = 0
                        for j in range(14):
                            sum += data[i + j]
                        if data[i + 14] != sum % 256:
                            _str = ""
                            for j in range(16):
                                _str += str(data[i + j]) + " "
                            print("校验失败", _str)
                            continue
                        self.speed = struct.unpack('<f', data[i + 4:i + 8])[0]
                        self.angle = struct.unpack('<f', data[i + 8:i + 12])[0]
                        self.id = struct.unpack('<H', data[i + 12:i + 14])[0]
                        print("当前ID", self.id)
                        if self.id==0:
                            is_finding_id=False
        #标识当前这一帧收到了变化，从最后面收到的时间反推
        print("设置与变化时间间隔：",current_recv_time-self.id*0.001-self.set_index_time)
        self.set_index_time=current_recv_time-self.id*0.001
        print(f"反算接受到的帧序号变化时间：{self.set_index_time}")



    def cmd_save_para(self):
        '''
        保存参数
        :return:
        '''
        time.sleep(2)
        send_cmd_bytes = [0xEB, 0x32, 0, 0, 0, 0, 0, 0, 0, 0xBE]
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        self.com.write(send_cmd_bytes)


    def cmd_set_position(self,set_position,delay_time=60):
        '''
        设置转的位置
        :return:
        '''
        send_cmd_bytes = [235, 1, 0, 0, 0, 0, 0, 0, 0, 190]
        send_cmd_bytes[2:6] = struct.pack('<f', set_position)
        # 计算校验和
        num = 0
        for i in range(8):
            num += send_cmd_bytes[i]
        send_cmd_bytes[8] = num % 256
        self.com.write(send_cmd_bytes)
        time.sleep(1)
        self.com.flushInput()
        is_on_position = False
        start_time = time.time()
        while True:
            # 需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            for i in range(len(data)):
                if data[i] == 0x55 and i + 15 < len(data) and data[i + 15] == 0xAA:
                    sum = 0
                    for j in range(14):
                        sum += data[i + j]
                    if data[i + 14] != sum % 256:
                        _str = ""
                        for j in range(16):
                            _str += str(data[i + j]) + " "
                        print("校验失败", _str)
                        continue

                    self.speed = struct.unpack('<f', data[i + 4:i + 8])[0]
                    self.angle = struct.unpack('<f', data[i + 8:i + 12])[0]
                    self.id = struct.unpack('<H', data[i + 12:i + 14])[0]
                    print("当前角度", self.angle)
                    #print(data[i + 2] & 0b1000)
                    # 修改角度比较逻辑，考虑角度循环特性
                    angle_diff = abs(self.angle - set_position)
                    angle_diff = min(angle_diff, 360 - angle_diff)  # 考虑角度循环
                    if ((data[i + 2] & 0b1000) > 0) or (math.fabs(self.speed)<0.1 and angle_diff < 0.05):#
                        is_on_position = True
                        break
            if is_on_position:
                print("云台已到达指定位置")
                print("当前角度", self.angle)
                break
            if time.time() - start_time > delay_time:
                print(f"等待{delay_time}s,退出找零")
                break
        #self.cmd_stop_all()
        if is_on_position:
            return True
        return False

    def start_read(self):
        self.packets_buffer.clear()
        self.is_recv_thread_running = True

        self.recv_thread = threading.Thread(target=self.recv_data)
        self.recv_thread.start()

    def stop_read(self):
        self.is_recv_thread_running = False


    def start_write(self, filename="t1.txt"):
        self.is_write_thread_running = True
        self.write_thread = threading.Thread(target=self.write_to_file, args=(filename,))
        self.write_thread.start()

    def stop_write(self):
        self.is_write_thread_running = False
        while self.write_thread.is_alive():
            time.sleep(1)

    def recv_data(self):
        '''
        接受数据，解析到内存中
        :return:
        '''
        while self.is_recv_thread_running:
            if self.com.in_waiting:
                data = self.com.read(self.com.in_waiting)  # 496
                for i in range(len(data)):
                    if data[i] == 0x55 and i + 15 < len(data) and data[i + 15] == 0xAA:
                        # #校验判断
                        sum=0
                        for j in range(14):
                            sum+=data[i+j]
                        if data[i + 14]!=sum%256:
                            _str=""
                            for j in range(16):
                                _str+=str(data[i+j])+" "
                            print("校验失败",_str)
                            continue
                        self.speed = struct.unpack('<f', data[i + 4:i + 8])[0]
                        self.angle = struct.unpack('<f', data[i + 8:i + 12])[0]
                        id=struct.unpack('<H', data[i + 12:i + 14])[0]
                        if (self.id-id)>60000:#超过了一个周期
                            id+=65536
                        self.id = id
                        self.packets_buffer.append(f"{self.speed} {self.angle} {self.id} {self.set_index_time+self.id*0.001}\n")


    def write_to_file(self,filename):
        with io.open(filename,"w") as f:
            while self.is_write_thread_running or len(self.packets_buffer)>0:
                buffer_num=len(self.packets_buffer)
                #print("buffer_num:",buffer_num)
                if buffer_num>0:
                    f.writelines(self.packets_buffer[0])
                    del self.packets_buffer[0]

class MinMotor1:##开环

    def __init__(self,com_name="/dev/ttyS7",bound_raito=115200):
        self.com = serial.Serial(com_name, bound_raito)
        print("串口状态：",self.com.is_open)
        self.speed=0.0#当前速度
        self.angle=0.0#当前角度
        self.CURRENT_MC = 3200# 当前电机的脉冲数，表示一圈
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


    def cmd_read_angle_current(self,delay_time=60):
        #读取实时的读数
        self.com.flushInput()
        self.com.flushOutput()
        self.com.write([0x01,0x36,0x6b])
        start_time = time.time()
        angle=0
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            # if len(data)>0:
            #     print(len(data))
            #     for i in range(len(data)):
            #         print('%#x'% data[i])
            if len(data)==8 and data[0]==0x01 and data[1]==0x36 and data[-1]==0x6b:
                angle = (data[3]<<24)|(data[4]<<16)|(data[5]<<8)|(data[6]<<0)
                angle =angle/65536*360
                if data[2] == 0x01:
                    angle=-angle
                #print(angle)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return angle

    def cmd_return_zero(self,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01, 0x9a, 0x00, 0x00, 0x6b])
        start_time = time.time()
        angle = 0
        while True:
            # 需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data) == 4 and data[0] == 0x01 and data[3] == 0x6b:
                if data[2] == 0x02:
                    print("正确返回")
                else:
                    print("错误命令")
                break
            if time.time() - start_time > delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return angle

    def cmd_set_en(self,state=0,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01,0xf3,state,0x00,0x6b])  # 设置使能 0，1
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
        self.com.flushOutput()
        self.com.write([0x01,0x31,0x6b])
        start_time = time.time()
        angle=0
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)==5 and data[0]==0x01 and data[4]==0x6b:
                print(data[2],data[3])
                angle = struct.unpack('>H', data[2:4])[0]#data[1]*(2<<8)+data[2]
                angle =angle/65536*360
                print(angle)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return angle

    def cmd_set_pos_ab(self,angle,speed=10,delay_time=60):
        '''
        转动相对角度
        :param direct:
        :param delay_time:
        :return:
        '''
#01 FD 01 05 DC 00 00 00 7D 00 00 00 6B
        send_cmd_bytes = [0x01,0xfd,0x01,0x05,0xdc,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x6b]

        send_cmd_bytes[3:5] = struct.pack('>H', int(speed))#速度1500rpm
        step=angle*128*200/360#/360*(200*64)#1280=36度目前
        print(int(step))
        direct=0
        if step<0:
            direct=1
        send_cmd_bytes[2] = direct  # 转的方向
        send_cmd_bytes[6:10] = struct.pack('>i', int(math.fabs(step)))  # 脉冲数

        #绝对位置
        self.com.flushInput()
        self.com.write(send_cmd_bytes)


        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)==4 and data[0]==0x01 and data[3]==0x6b:
                print(data[1],data[2])
                if data[2]==0x02:
                    print("正确返回")
                    return True
                elif data[2]==0xe2:
                    print("条件不满足")
                    return False
                else:
                    print("错误命令")
                    return False
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break


    def cmd_set_xf(self,xf=64,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01,0x84,0x8a,0x01,xf,0x6b])
        start_time = time.time()
        angle=0
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)==4 and data[0]==0x01 and data[3]==0x6b:
                if data[2] == 0x02:
                    print("正确返回")
                else:
                    print("错误命令")
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return angle

    def cmd_set_pos(self,input_angle,delay_time=60):
        '''
        PID转动目标角度
        :param input_angle:
        :param delay_time:
        :return:
        '''
        # if angle<-135 or angle>135:
        #     print("角度只能是-135~135")
        #     return False

        print(f"-----------输入的转动角度：{input_angle}")
        start_angle = self.cmd_read_angle()  # 获取当前角度
        print(f"当前角度:{start_angle}")
        dist_angle=start_angle+input_angle#目标角度
        if dist_angle<0:
            dist_angle+=360
        if dist_angle>360:
            dist_angle -= 360
        print(f"-----------目标角度：{dist_angle}")
        protect_num = 0
        same_angle_num=0
        self.cmd_set_pos_ab(input_angle)#先转一次，然后再启动pid
        last_angle=0
        start_time=time.time()
        while time.time()-start_time<delay_time:
            if protect_num>1:
                print("-----------多次触发限位保护，检查输入参数！！！！！！！！！！")
                break
            if same_angle_num > 3:
                print("多次转动后角度无变化，请返回上层目录用【解除堵转（含重启小电机）】处理")
                break

            time.sleep(1)
            start_angle = self.cmd_read_angle()
            if start_angle < 0:
                start_angle += 360
            print(f"当前角度:{start_angle}")
            if math.fabs(last_angle-start_angle) <0.001:#转完之后没有动：
                same_angle_num+=1

            last_angle=start_angle
            if math.fabs(start_angle - dist_angle) < 0.1:  # 误差0.1之类就表示到达了
                print("-----------转动到指定角度，转动完成")
                break

            step_angle=dist_angle-start_angle
            if step_angle>180:#解决跨360的问题
                step_angle-=360
            if step_angle<-180:
                step_angle+=360
            #控制旋转
            time.sleep(1)
            print(f"转动角度:{step_angle}")
            if (not self.cmd_set_pos_ab(step_angle)):
                print("触发限位，解除保护...")
                self.cmd_reset_protect()#如果报错了需要接触保护
                protect_num+=1

        # if math.fabs(start_angle - dist_angle) >= 0.1:  # 误差0.1之类就表示到达了
        #     print("-----------规定时间未转动到指定位置，转动失败！！！！！！！！！！")
        # print("-------------------耗时",time.time()-start_time)


    def cmd_reset_protect(self,delay_time=60):
        '''
        解除堵转保护
        :return:
        '''
        self.com.flushInput()
        self.com.write([0x01, 0x0e, 0x52, 0x6b])
        start_time = time.time()
        state = False
        while True:
            # 需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data) == 4 and data[0] == 0x01 and data[3] == 0x6b:
                if data[2] == 0x02:
                    print("正确返回")
                    state = True
                else:
                    print("错误命令")
                break
            if time.time() - start_time > delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return state


    def cmd_set_open(self,delay_time=10):
        '''
        设置为开环模式
        :return:
        '''
        self.com.flushInput()
        self.com.write([0x01,0x46,0x69,0x01,0x01,0x6b]) #开环指令
        #self.com.write([0x01, 0x46, 0x69, 0x01, 0x02, 0x6b])#闭环的指令
        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)==4 and data[0]==0x01 and data[3]==0x6b:
                if data[2] == 0x02:
                    print("正确返回")
                else:
                    print("错误命令")
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break


    def cmd_set_open_current(self, current_mA, save=False, delay_time=10):
        '''
        设置开环模式的工作电流
        :param current_mA: 电流值，单位为毫安(mA)
        :param save: 是否存储设置(断电后是否保留)，默认False(不存储)
        :param delay_time: 等待响应的超时时间，默认10秒
        :return:
        '''
        # 限制电流范围(根据实际设备规格可能需要调整)
        if current_mA < 0 or current_mA > 65535:
            print("电流值超出范围(0-65535mA)")
            return

        # 构造命令帧
        save_flag = 0x01 if save else 0x00  # 是否存储标志
        current_bytes = struct.pack('>H', int(current_mA))  # 将电流值打包为2字节大端格式

        send_cmd_bytes = [0x01, 0x44, 0x33, save_flag, current_bytes[0], current_bytes[1], 0x6b]
        print(send_cmd_bytes)
        self.com.flushInput()
        self.com.write(send_cmd_bytes)

        start_time = time.time()
        while True:
            data = self.com.read(self.com.in_waiting)
            #print(data)
            if len(data) == 4 and data[0] == 0x01 and data[1] == 0x44 and data[3] == 0x6b:
                if data[2] == 0x02:
                    print("设置开环电流成功，电流值: {}mA".format(current_mA))
                else:
                    print("设置开环电流失败，错误代码: %#x" % data[2])
                break
            if time.time() - start_time > delay_time:
                print(f"等待{delay_time}s超时，设置开环电流失败")
                break

    def detect_limit_switches(self, max_rotation=300, delay_time=60):
        """
        通过相对旋转和读取绝对位置的方式检测左右限位开关状态

        :param max_rotation: 最大旋转角度（防止无限旋转）
        :param delay_time: 超时时间
        :return: dict 包含左右限位状态
        """
        print("开始检测限位开关...")

        # 先获取当前位置作为中间位置
        initial_angle = self.cmd_read_angle()
        print(f"初始位置角度: {initial_angle}")

        left_limit_reached = False
        right_limit_reached = False
        left_limit_angle = None
        right_limit_angle = None

        # 向左旋转检测左限位
        print("向左旋转检测左限位...")
        test_angle = -5  # 每次旋转角度
        total_rotated = 0

        while abs(total_rotated) < max_rotation:
            # 记录旋转前的角度
            before_angle = self.cmd_read_angle()

            # 尝试向左旋转
            result = self.cmd_set_pos_ab(test_angle)
            time.sleep(0.5)  # 等待稳定

            # 读取旋转后的角度
            after_angle = self.cmd_read_angle()

            # 如果角度没有变化或变化很小，可能是触发了限位
            angle_diff = after_angle - before_angle
            # 处理跨越0度的情况
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360

            print(f"尝试旋转{test_angle}度，实际角度变化: {angle_diff}")

            # 如果实际旋转角度与期望角度相差较大，可能触发限位
            if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，认为可能触发限位
                print("检测到左限位可能已触发")
                left_limit_reached = True
                left_limit_angle = after_angle
                break

            total_rotated += test_angle

            # 如果返回错误状态，说明触发限位
            if not result:
                print("左限位触发")
                left_limit_reached = True
                left_limit_angle = after_angle
                # 解除保护
                #self.cmd_reset_protect()
                break

        # 回到初始位置附近
        if left_limit_reached:
            print("已检测到左侧限位，转到右侧限位附近...")
            self.cmd_set_pos_ab(250)
            time.sleep(5)
        else:
            # 如果未检测到左限位，回到初始位置
            print("检测失败，返回初始位置...")
            self.cmd_set_pos_ab(-total_rotated)
            time.sleep(1)

        # 重新获取当前位置
        current_angle = self.cmd_read_angle()
        print(f"当前位置角度: {current_angle}")
        total_rotated = 0

        # 向右旋转检测右限位
        print("向右旋转检测右限位...")
        test_angle = 5  # 每次旋转角度

        while abs(total_rotated) < max_rotation:
            # 记录旋转前的角度
            before_angle = self.cmd_read_angle()

            # 尝试向右旋转
            result = self.cmd_set_pos_ab(test_angle)
            time.sleep(0.5)  # 等待稳定

            # 读取旋转后的角度
            after_angle = self.cmd_read_angle()

            # 如果角度没有变化或变化很小，可能是触发了限位
            angle_diff = after_angle - before_angle
            # 处理跨越0度的情况
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360

            print(f"尝试旋转{test_angle}度，实际角度变化: {angle_diff}")

            # 如果实际旋转角度与期望角度相差较大，可能触发限位
            if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，认为可能触发限位
                print("检测到右限位可能已触发")
                right_limit_reached = True
                right_limit_angle = after_angle
                break

            total_rotated += test_angle

            # 如果返回错误状态，说明触发限位
            if not result:
                print("右限位触发")
                right_limit_reached = True
                right_limit_angle = after_angle
                # 解除保护
                self.cmd_reset_protect()
                break

        # 回到中间位置
        #print("返回中间位置...")

        # # 再从起始点回到中间位置
        # current_angle = self.cmd_read_angle()
        # # 计算中间角度，考虑跨越0度的情况
        # if left_limit_angle is not None and right_limit_angle is not None:
        #     total_angle=(360-left_limit_angle)+right_limit_angle#总的行程
        #     angle_to_middle=-total_angle/2
        #     middle_angle = right_limit_angle+angle_to_middle
        #     if middle_angle<0:
        #         middle_angle+=360
        # else:
        #     # 如果没有检测到限位，则使用初始位置作为中间位置
        # #     middle_angle = initial_angle
        # #     angle_to_middle = middle_angle - current_angle
        #
        # print(f"从当前位置 {current_angle} 度转到中间位置 {middle_angle} 度，需要转动 {angle_to_middle} 度")
        # self.cmd_set_pos_ab(angle_to_middle)
        # time.sleep(3)

        final_angle = self.cmd_read_angle()
        print(f"最终位置角度: {final_angle}")

        # 返回检测结果
        result = {
            "left_limit_reached": left_limit_reached,
            "right_limit_reached": right_limit_reached,
            "left_limit_angle": left_limit_angle,
            "right_limit_angle": right_limit_angle,
            "initial_angle": initial_angle,
            "final_angle": final_angle
        }

        print("限位检测结果:")
        print(f"  初始位置: {initial_angle}")
        print(f"  左限位: {'触发' if left_limit_reached else '未触发'}")
        if left_limit_angle is not None:
            print(f"    触发角度: {left_limit_angle}")
        print(f"  右限位: {'触发' if right_limit_reached else '未触发'}")
        if right_limit_angle is not None:
            print(f"    触发角度: {right_limit_angle}")
        print(f"  最终位置: {final_angle}")

        return result


class MinMotor:  #########闭环小电机

    def __init__(self,com_name="/dev/ttyS7",bound_raito=115200):
        self.com = serial.Serial(com_name, bound_raito)
        print("串口状态：",self.com.is_open)
        self.speed=0.0#当前速度
        self.angle=0.0#当前角度
        self.CURRENT_MC = 3200# 当前电机的脉冲数，表示一圈
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


    def cmd_read_angle_current(self,delay_time=60):
        #读取实时的读数
        self.com.flushInput()
        self.com.flushOutput()
        self.com.write([0x01,0x36,0x6b])
        start_time = time.time()
        angle=0
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            # if len(data)>0:
            #     print(len(data))
            #     for i in range(len(data)):
            #         print('%#x'% data[i])
            if len(data)==8 and data[0]==0x01 and data[1]==0x36 and data[-1]==0x6b:
                angle = (data[3]<<24)|(data[4]<<16)|(data[5]<<8)|(data[6]<<0)
                angle =angle/65536*360
                if data[2] == 0x01:
                    angle=-angle
                #print(angle)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return angle

    def cmd_return_zero(self,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01, 0x9a, 0x00, 0x00, 0x6b])
        start_time = time.time()
        angle = 0
        while True:
            # 需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data) == 4 and data[0] == 0x01 and data[3] == 0x6b:
                if data[2] == 0x02:
                    print("正确返回")
                else:
                    print("错误命令")
                break
            if time.time() - start_time > delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return angle

    def cmd_set_en(self,state=0,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01,0xf3,state,0x00,0x6b])  # 设置使能 0，1
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
        self.com.flushOutput()
        self.com.write([0x01,0x31,0x6b])
        start_time = time.time()
        angle=0
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)==5 and data[0]==0x01 and data[4]==0x6b:
                print(data[2],data[3])
                angle = struct.unpack('>H', data[2:4])[0]#data[1]*(2<<8)+data[2]
                angle =angle/65536*360
                print(angle)
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return angle

    def cmd_set_pos_ab(self,angle,speed=20,delay_time=60):
        '''
        转动相对角度
        :param direct:
        :param delay_time:
        :return:
        '''
#01 FD 01 05 DC 00 00 00 7D 00 00 00 6B
        send_cmd_bytes = [0x01,0xfd,0x01,0x05,0xdc,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x6b]

        send_cmd_bytes[3:5] = struct.pack('>H', int(speed))#速度1500rpm
        step=angle*128*200/360#/360*(200*64)#1280=36度目前
        print(int(step))
        direct=0
        if step<0:
            direct=1
        send_cmd_bytes[2] = direct  # 转的方向
        send_cmd_bytes[6:10] = struct.pack('>i', int(math.fabs(step)))  # 脉冲数

        #绝对位置
        self.com.flushInput()
        self.com.write(send_cmd_bytes)


        start_time = time.time()
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)==4 and data[0]==0x01 and data[3]==0x6b:
                print(data[1],data[2])
                if data[2]==0x02:
                    print("正确返回")
                    return True
                elif data[2]==0xe2:
                    print("条件不满足")
                    return False
                else:
                    print("错误命令")
                    return False
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break


    def cmd_set_xf(self,xf=64,delay_time=60):
        self.com.flushInput()
        self.com.write([0x01,0x84,0x8a,0x01,xf,0x6b])
        start_time = time.time()
        angle=0
        while True:
            #需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data)==4 and data[0]==0x01 and data[3]==0x6b:
                if data[2] == 0x02:
                    print("正确返回")
                else:
                    print("错误命令")
                break
            if time.time()-start_time>delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return angle

    def cmd_set_pos(self,input_angle,delay_time=60):
        '''
        PID转动目标角度
        :param input_angle:
        :param delay_time:
        :return:
        '''
        # if angle<-135 or angle>135:
        #     print("角度只能是-135~135")
        #     return False

        print(f"-----------输入的转动角度：{input_angle}")
        start_angle = self.cmd_read_angle()  # 获取当前角度
        print(f"当前角度:{start_angle}")
        dist_angle=start_angle+input_angle#目标角度
        if dist_angle<0:
            dist_angle+=360
        if dist_angle>360:
            dist_angle -= 360
        print(f"-----------目标角度：{dist_angle}")
        protect_num = 0
        same_angle_num=0
        self.cmd_set_pos_ab(input_angle)#先转一次，然后再启动pid
        last_angle=0
        start_time=time.time()
        while time.time()-start_time<delay_time:
            if protect_num>1:
                print("-----------多次触发限位保护，检查输入参数！！！！！！！！！！")
                break
            if same_angle_num > 3:
                print("多次转动后角度无变化，请返回上层目录用【解除堵转（含重启小电机）】处理")
                break

            time.sleep(1)
            start_angle = self.cmd_read_angle()
            if start_angle < 0:
                start_angle += 360
            print(f"当前角度:{start_angle}")
            if math.fabs(last_angle-start_angle) <0.001:#转完之后没有动：
                same_angle_num+=1

            last_angle=start_angle
            if math.fabs(start_angle - dist_angle) < 0.1:  # 误差0.1之类就表示到达了
                print("-----------转动到指定角度，转动完成")
                break

            step_angle=dist_angle-start_angle
            if step_angle>180:#解决跨360的问题
                step_angle-=360
            if step_angle<-180:
                step_angle+=360
            #控制旋转
            time.sleep(1)
            print(f"转动角度:{step_angle}")
            if (not self.cmd_set_pos_ab(step_angle)):
                print("触发限位，解除保护...")
                self.cmd_reset_protect()#如果报错了需要接触保护
                protect_num+=1

        if math.fabs(start_angle - dist_angle) >= 0.1:  # 误差0.1之内就表示到达了
            print("-----------规定时间未转动到指定位置，转动失败！！！！！！！！！！")
        print("-------------------耗时",time.time()-start_time)

    def cmd_reset_protect(self,delay_time=60):
        '''
        解除堵转保护
        :return:
        '''
        self.com.flushInput()
        self.com.write([0x01, 0x0e, 0x52, 0x6b])
        start_time = time.time()
        state = False
        while True:
            # 需要判断是否已经过零
            data = self.com.read(self.com.in_waiting)
            if len(data) == 4 and data[0] == 0x01 and data[3] == 0x6b:
                if data[2] == 0x02:
                    print("正确返回")
                    state = True
                else:
                    print("错误命令")
                break
            if time.time() - start_time > delay_time:
                print(f"等待{delay_time}s,退出")
                break
        return state

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


def kill_app_process():
    '''
    关闭app进程
    :return:
    '''
    command = "ps -A | grep app"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout = str(process.communicate())
    print(stdout)
    stdout0 = stdout.strip().split()
    command1 = rf"kill -9 {stdout0[1]}"
    print(command1)
    process1 = subprocess.Popen(command1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout1 = process1.communicate()

def configurate_all():
    print("运行power_on_all.sh")
    command0 = rf"/app/power_on_all.sh"
    process0 = subprocess.Popen(command0, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout0 = process0.communicate()
    print("等待雷达上电中......")
    time.sleep(30)

    print("运行device_settings.py")
    command3 = rf"python3 /app/device_settings.py"
    process2 = subprocess.Popen(command3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout2 = process2.communicate()
    time.sleep(50)
    print(stdout2)


def set_ptp():#重要
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=set&object=lidar&key=clock_source&value=1")
    #print(result.status_code)  # 请求状态
    #print(result.url)  # 请求url
    print(result.text)  # 请求结果
    if "Success" in result.text:
        return True
    else:
        return False

def set_return_mode():
    result = requests.get(url="http://192.168.1.201/pandar.cgi?action=set&object=lidar_data&key=lidar_mode&value=1")
    print(result.text)
    if "Success" in result.text:
        return True
    else:
        return False

def lidar_setting():
    '''
    检查IP，配置PTP和回波模式
    :return:
    '''
    setting_signal=True
    print("----------------------1.检查雷达连接，需先确保雷达已上电")
    if os.system('ping -c 1 -w 1 192.168.1.201')==0:
        print("\033[92m%s\033[0m" % "----------------------雷达网络正常")

    else:
        print("\033[91m%s\033[0m" % "----------------------雷达网络错误")
        setting_signal = False
    print("----------------------2.设置雷达PTP授时")
    if set_ptp():

        print("\033[92m%s\033[0m" % "----------------------雷达PTP授时设置成功")

    else:
        print("\033[91m%s\033[0m" % "----------------------雷达PTP授时设置失败")
        setting_signal = False
    print("----------------------3.设置雷达回波模式")
    if set_return_mode():

        print("\033[92m%s\033[0m" % "----------------------雷达PTP回波模式设置成功")
    else:
        print("\033[91m%s\033[0m" % "----------------------雷达PTP回波模式设置失败")
        setting_signal = False
    return setting_signal

if __name__ == "__main__":

    with open("模块功能测试.txt",'a',encoding="utf-8") as file:

        times=datetime.now()
        date=times.strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{date} 功能测试")
        file.flush()
        kill_app_process()

        configurate_all()

        fail_message=""
        success_message=""
        test_success=0
        test_fail = 0
        while True:

            a=('################################检查设备配置################################\n'
                  '[0]：测试所有功能\n'
                  '[1]：测试转台\n'
                  '[2]：测试小电机旋转测试\n'
                  '[3]：小电机旋转测试测试激光点,######需要人眼观察激光有无异常#######\n'
                  '[4]：测试雷达\n' 
                  '[5]：测试相机\n'
                  '[x]：退出\n')
            print(a)
            file.write(a)
            file.flush()
            choose_number0 = input("选择功能：\n")
            file.write(f"选择功能:{choose_number0} \n")
            file.flush()

            if choose_number0 == "0":
                ###转台寻零
                print("#########################测试转台########################################\n")
                print("#########################转台寻零#################\n")
                file.write("#########################测试转台########################################\n")
                file.flush()
                file.write("#########################转台寻零#################\n")
                file.flush()
                mo=Motor()
                status = mo.cmd_find_zero()  # 转台寻零
                if status == False:
                    print("转台寻零失败\n")
                    file.write("转台寻零失败\n")
                    file.flush()
                    test_fail +=1
                    fail_message = fail_message + f"{test_fail}.转台寻零失败\n"
                else:
                    test_success +=1
                    success_message = f"{test_success}.转台寻零成功\n"
                    file.write("转台寻零成功\n")
                    file.flush()
                #####固定角度旋转测试
                print("#########################固定40度进行旋转测试#################\n")
                file.write("#########################固定40度进行旋转测试#################\n")
                file.flush()
                angles_list = [0,40, 80, 120, 160, 200, 240, 280, 320, 0, 179, 0, 182, 0, 179, 182, 0]
                for angles in angles_list:
                    print(f"转台旋转测试到{angles}度")
                    status1 = mo.cmd_set_position(angles)  # 转台旋转测试到指定位置
                    if status1 == False:
                        status = False
                        print(f"{angles}转台旋转测试失败\n")
                        file.write(f"{angles}转台旋转测试失败\n")
                        file.flush()
                    time.sleep(2)
                if status == False:
                    print("转台旋转测试失败\n")
                    file.write("转台旋转测试失败\n")
                    file.flush()
                    test_fail +=1
                    fail_message = fail_message + f"{test_fail}.转台旋转测试失败\n"
                else:
                    test_success +=1
                    success_message = success_message + f"{test_success}.转台旋转测试成功\n"
                    file.write("转台旋转测试成功\n")
                    file.flush()


                #####手动输入角度旋转测试
                print("#########################手动旋转测试#################\n")
                file.write("#########################手动旋转测试#################\n")
                file.flush()
                while True:
                    rotate_angle = input("请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                    file.write("请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                    file.flush()
                    file.write(rotate_angle)
                    file.flush()
                    if rotate_angle == 'x':
                        break
                    try:
                        rotate_angle = float(rotate_angle)
                        status1 = mo.cmd_set_position(rotate_angle)
                        if status1 == False:
                            status = False
                            print(f"{rotate_angle}手动旋转失败\n")
                            file.write(f"{rotate_angle}手动旋转失败\n")
                            file.flush()
                        else:
                            test_success +=1
                            print(f"{rotate_angle}手动旋转成功\n")
                            file.write(f"{rotate_angle}手动旋转成功\n")
                            file.flush()

                    except:
                        print("字符无法识别：请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                        file.write("字符无法识别：请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                        file.flush()
                if status == False:
                    test_fail +=1
                    fail_message = fail_message + f"{test_fail}.手动转台旋转测试失败\n"
                    file.write("手动转台旋转测试失败\n")
                    file.flush()
                else:
                    test_success +=1
                    success_message = success_message + f"{test_success}.手动转台旋转测试成功\n"
                    file.write("手动转台旋转测试成功\n")
                    file.flush()


                ###测试小电机
                print("#########################测试小电机#################\n")
                file.write("#########################测试小电机#################\n")
                file.flush()
                file.write("#####################测试小电机旋转测试####################\n")
                file.flush()
                command0 = "echo 1 > /proc/rp_power/laser"
                file.write("echo 1 > /proc/rp_power/laser:打开激光\n")
                file.flush()
                process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            shell=True, text=True)
                process0.communicate()

                error_signal = False
                test_signal = 0
                mon = MinMotor1()
                limits = mon.detect_limit_switches()
                lefts_limits = limits['left_limit_angle']
                print(f"左限位角度:{lefts_limits}\n")
                file.write(f"左限位角度:{lefts_limits}\n")
                file.flush()
                right_limits = limits['right_limit_angle']
                file.write(f"右限位角度:{right_limits}\n")
                file.flush()
                print(f"右限位角度:{right_limits}\n")
                while not error_signal:
                    total_angle_limits = 360 - lefts_limits + right_limits
                    print(f"小电机左右限位的总角度：{total_angle_limits}\n")
                    if 270 < total_angle_limits < 280:
                        print("小电机限位角度正常\n")
                        file.write("小电机限位角度正常\n")
                        file.flush()

                    else:
                        print("小电机左右限位角度异常，出现堵转\n")
                        error_signal = True
                        test_fail+=1
                        fail_message = fail_message + "小电机左右限位角度异常，出现堵转\n"
                        file.write("小电机左右限位角度异常，出现堵转\n")
                        file.flush()
                        break

                    current_angle = mon.cmd_read_angle()
                    total_angle_limits = total_angle_limits + 3
                    # 转至左限位
                    print("小电机左限位转动中......\n")
                    file.write("小电机左限位转动中......\n")
                    file.flush()
                    mon.cmd_set_pos_ab(-total_angle_limits)
                    time.sleep(8)
                    after_angle = mon.cmd_read_angle()
                    print(f"往左转停角度{after_angle}\n")
                    file.write(f"往左转停角度{after_angle}\n")
                    file.flush()
                    if abs(lefts_limits - after_angle) < 2:  # 左限位小电机旋转
                        # 转至右限位
                        print("小电机右限位转动中......\n")
                        file.write("小电机右限位转动中......\n")
                        file.flush()
                        mon.cmd_set_pos_ab(total_angle_limits)
                        time.sleep(8)
                        after_angle = mon.cmd_read_angle()
                        print(f"往右转停角度{after_angle}\n")
                        file.write(f"往右转停角度{after_angle}\n")
                        file.flush()
                        if abs(right_limits - after_angle) < 2:
                            print("小电机大角度旋转正常\n")
                            file.write("小电机大角度旋转正常\n")
                            file.flush()
                        else:
                            print("右限位小电机堵转\n")
                            file.write("右限位小电机堵转\n")
                            file.flush()
                            error_signal = True
                            break
                    else:
                        print("左限位小电机堵转\n")
                        error_signal = True
                        test_fail+=1
                        fail_message = fail_message + f"{test_fail}.小电机向左旋转测试失败，堵转\n"
                        file.write("小电机向左旋转测试失败，堵转\n")
                        file.flush()
                        break
                    # 小角度验证
                    total_rotated = 0
                    max_rotation = 300
                    test_angle = -5
                    # 转至左限位
                    print("小电机左限位转动中......\n")
                    file.write("小电机左限位转动中......\n")
                    file.flush()

                    while abs(total_rotated) < max_rotation:
                        before_angle = mon.cmd_read_angle()
                        print(f"小角度旋转前当前角度:{before_angle}\n")
                        mon.cmd_set_pos_ab(test_angle)
                        time.sleep(1)
                        after_angle = mon.cmd_read_angle()
                        print(f"小角度旋转后当前角度:{after_angle}\n")
                        angle_diff = after_angle - before_angle

                        if angle_diff > 180:
                            angle_diff -= 360
                        elif angle_diff < -180:
                            angle_diff += 360
                        print(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}\n")
                        if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，触发限位，可能触发限位
                            if abs(after_angle - lefts_limits) < 3:  # 是否到达左限位
                                print("检测左限位已触发\n")
                                mon.cmd_set_pos_ab(-test_angle)
                                break
                            else:
                                error_signal = True
                                print("小电机堵转\n")
                                print(f"左限位角度:{lefts_limits}\n")
                                break

                        total_rotated += test_angle
                    if error_signal:
                        print("小电机堵转\n")
                        test_fail+=1
                        fail_message = fail_message + f"{test_fail}.小电机旋转测试失败,转至左限位堵转\n"
                        file.write("小电机旋转测试失败,转至左限位堵转\n")
                        file.flush()
                        break
                    # 转至右限位
                    total_rotated = 0
                    max_rotation = 300
                    test_angle = 5
                    # 转至右限位
                    print("小电机右限位转动中......\n")
                    file.write("小电机右限位转动中......\n")
                    file.flush()
                    while abs(total_rotated) < max_rotation:
                        before_angle = mon.cmd_read_angle()
                        print(f"小角度旋转前当前角度:{before_angle},此时有可能从左限位往右转了5度，也可能未转动\n")
                        mon.cmd_set_pos_ab(test_angle)
                        time.sleep(1)
                        after_angle = mon.cmd_read_angle()
                        print(f"小角度旋转后当前角度:{after_angle}\n")
                        angle_diff = after_angle - before_angle
                        if angle_diff > 180:
                            angle_diff -= 360
                        elif angle_diff < -180:
                            angle_diff += 360
                        print(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}\n")
                        if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，可能触发限位
                            if abs(after_angle - right_limits) < 3:  # 是否到达右限位
                                print("检测右限位已触发\n")
                                mon.cmd_set_pos_ab(-90)
                                break
                            else:
                                error_signal = True
                                print("小电机堵转\n")
                                print(f"右限位角度:{right_limits}\n")
                                break
                        total_rotated += test_angle
                    if error_signal:
                        print("小电机堵转\n")
                        test_fail+=1
                        fail_message = fail_message + f"{test_fail}.小电机旋转测试失败,转至右限位堵转\n"
                        file.write("小电机旋转测试失败,转至右限位堵转\n")
                        file.flush()
                        break
                    else:
                        print("小电机旋转测试成功\n")
                        test_success +=1
                        success_message = success_message + f"{test_success}.小电机旋转测试成功\n"
                        file.write("小电机旋转测试成功\n")
                        file.flush()
                        break

                ####测试激光灯大小
                print("#########################测试激光灯旋转测试#################\n")
                file.write("#########################测试激光灯旋转测试#################\n")
                file.flush()
                command0 = "echo 1 > /proc/rp_power/laser\n"
                file.write("echo 1 > /proc/rp_power/laser:打开激光\n")
                file.flush()
                process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            shell=True, text=True)
                process0.communicate()
                error_signal = False
                test_signal = 0
                mon = MinMotor1()
                limits = mon.detect_limit_switches()
                lefts_limits = limits['left_limit_angle']
                print(f"左限位角度:{lefts_limits}\n")
                file.write(f"左限位角度:{lefts_limits}\n")
                file.flush()
                right_limits = limits['right_limit_angle']
                print(f"右限位角度:{right_limits}\n")
                file.write(f"右限位角度:{right_limits}\n")
                file.flush()
                while not error_signal:
                    # 小角度验证
                    total_rotated = 0
                    max_rotation = 300
                    test_angle = -2
                    # 转至左限位
                    print("小电机左限位转动中......\n")
                    file.write("小电机左限位转动中......\n")
                    file.flush()
                    while abs(total_rotated) < max_rotation:
                        before_angle = mon.cmd_read_angle()
                        print(f"小角度旋转前当前角度:{before_angle}\n")
                        file.write(f"小角度旋转前当前角度:{before_angle}\n")
                        file.flush()
                        mon.cmd_set_pos_ab(test_angle)
                        time.sleep(1)
                        after_angle = mon.cmd_read_angle()
                        print(f"小角度旋转后当前角度:{after_angle}\n")
                        file.write(f"小角度旋转后当前角度:{after_angle}\n")
                        file.flush()
                        angle_diff = after_angle - before_angle

                        if angle_diff > 180:
                            angle_diff -= 360
                        elif angle_diff < -180:
                            angle_diff += 360
                        print(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}\n")
                        file.write(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}\n")
                        file.flush()
                        if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，触发限位，可能触发限位
                            if abs(after_angle - lefts_limits) < 3:  # 是否到达左限位
                                print("检测左限位已触发\n")
                                file.write("检测左限位已触发\n")
                                file.flush()
                                mon.cmd_set_pos_ab(-test_angle*2)
                                time.sleep(2)
                                break
                            else:
                                error_signal = True
                                print("测试激光，小电机旋转堵转\n")
                                file.write("测试激光，小电机旋转堵转\n")
                                file.flush()
                                print(f"左限位角度:{lefts_limits}\n")

                                break

                        total_rotated += test_angle
                    if error_signal:
                        test_fail+=1
                        fail_message = fail_message + f"{test_fail}.测试激光灯旋转测试失败,转至左限位堵转\n"
                        file.write("测试激光灯旋转测试失败,转至左限位堵转\n")
                        file.flush()
                        print("测试激光，小电机旋转堵转\n")
                        break
                    # 转至右限位

                    total_rotated = 0
                    max_rotation = 300
                    test_angle = 2
                    # 转至右限位
                    print("小电机右限位转动中......\n")
                    file.write("小电机右限位转动中......\n")
                    file.flush()
                    while abs(total_rotated) < max_rotation:
                        mon.cmd_set_pos_ab(test_angle)
                        before_angle = mon.cmd_read_angle()
                        print(f"小角度旋转前当前角度:{before_angle}\n")
                        file.flush()
                        file.write(f"小角度旋转前当前角度:{before_angle}\n")
                        mon.cmd_set_pos_ab(test_angle)
                        time.sleep(1)
                        after_angle = mon.cmd_read_angle()
                        print(f"小角度旋转后当前角度:{after_angle}\n")
                        file.write(f"小角度旋转后当前角度:{after_angle}\n")
                        file.flush()
                        angle_diff = after_angle - before_angle
                        if angle_diff > 180:
                            angle_diff -= 360
                        elif angle_diff < -180:
                            angle_diff += 360
                        print(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}\n")
                        file.write(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}\n")
                        file.flush()
                        if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，可能触发限位
                            if abs(after_angle - right_limits) < 3:  # 是否到达右限位
                                print("检测右限位已触发\n")
                                file.write("检测右限位已触发\n")
                                file.flush()
                                mon.cmd_set_pos_ab(-total_angle_limits / 2)
                                break
                            else:
                                error_signal = True
                                print("测试激光，小电机旋转堵转\n")
                                file.write("测试激光灯旋转测试失败,转至右限位堵转\n")
                                file.flush()
                                print(f"右限位角度:{right_limits}")
                                file.write(f"右限位角度:{right_limits}\n")
                                file.flush()
                                break
                        total_rotated += test_angle
                    if error_signal:
                        print("测试激光，小电机旋转堵转\n")
                        test_fail += 1
                        fail_message = fail_message + f"{test_fail}.测试激光灯旋转测试失败,转至右限位堵转\n"
                        file.write("测试激光，小电机旋转堵转\n")
                        file.flush()
                        break
                    else:
                        print("测试激光，小电机旋转完成\n")
                        test_success += 1
                        success_message = success_message + f"{test_success}.测试激光，小电机旋转完成\n"
                        file.write("测试激光，小电机旋转完成\n")
                        file.flush()
                        break

                ###测试雷达
                file.write("#####################雷达测试####################\n")
                file.flush()
                result = lidar_setting()
                if not result:
                    print("雷达配置失败\n")
                    test_fail += 1
                    fail_message = fail_message + f"{test_fail}.测试雷达失败\n"
                    file.write("测试雷达失败\n")
                    file.flush()
                else:
                    print("测试雷达成功")
                    test_success += 1
                    success_message = success_message + f"{test_success}.测试雷达成功\n"
                    file.write("测试雷达成功\n")
                    file.flush()

                ###测试相机拍照
                print("#########################测试拍照#################\n")
                file.write("#########################测试拍照#################\n")
                count0 = 0
                for filename in os.listdir('/app'):
                    if filename.lower().endswith('.jpg'):
                        count0 += 1
                print(f"当前相机照片{count0}张\n")
                file.write(f"当前相机照片{count0}张\n")
                # 开相机
                command0 = "echo 1 > /sys/control/power_camera1 && echo 1 > /sys/control/camera_power1" \
                           "&&echo 1 > /sys/control/power_camera2 && echo 1 > /sys/control/camera_power2"  # 检查开机时，相机是否已经连接
                process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True, text=True)
                process0.communicate()
                time.sleep(10)

                command1 = "lsusb | grep 'Sony' "  # 检查开机时，相机是否已经连接
                process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True, text=True)
                stdout1 = process1.communicate()[0]
                print(f"相机返回：{stdout1}")

                file.write(f"查看相机：lsusb | grep 'Sony'：{stdout1}\n")
                time.sleep(3)

                # with open("camera_number.txt", 'a', encoding='utf-8') as file:
                # file.write(stdout1)
                sony_num = stdout1.count("Sony")
                print(f"sony出现次数：{sony_num}\n")

                if sony_num == 2:
                    print("相机全部开启\n")
                    file.write("相机全部开启\n")
                else:
                    print("存在相机开启失败\n")
                    file.write("有相机开启失败\n")
                    test_fail += 1
                    fail_message = fail_message + f"{test_fail}.相机开启失败\n"

                command2 = "/app/CrSDK/build/RemoteCli-test"  # 检查开机时，相机是否已经连接
                process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True, text=True)
                process2.stdin.write("\n")
                process2.stdin.flush()

                # 立即继续执行，不等待进程结束
                time.sleep(20)

                count1 = 0
                for filename in os.listdir('/app'):
                    if filename.lower().endswith('.jpg'):
                        count1 += 1
                print(f"当前相机照片{count1}张\n")
                file.write(f"再次检查相机照片{count1}张\n")
                if count1 == count0 + 2:
                    print("相机拍照功能正常\n")
                    test_success += 1
                    file.write("相机拍照功能正常\n")
                    success_message = success_message + f"{test_success}.相机拍照成功\n"

                else:
                    print("控制相机拍照失败，请再次进行测试\n")
                    test_fail += 1
                    file.write("控制相机拍照失败，请再次进行测试\n")
                    fail_message = fail_message + f"{test_fail}.控制相机拍照失败，请再次进行测试\n"

                print("\n\n\n")
                print("测试结果为：\n\n")
                print(f"测试通过：{test_success}个测试\n分别是：\n{success_message}\n\n")
                print(f"测试失败：{test_fail}个测试\n分别是：\n{fail_message}\n\n")

                print("可单独测试失败的测试项")


                file.write("测试结果为：\n\n")
                file.write(f"测试通过：{test_success}个测试\n分别是：{success_message}\n\n")
                file.write(f"测试失败：{test_fail}个测试\n分别是：{fail_message}\n\n")


            elif choose_number0 == "1":  #测试转台

                file.write("#########################测试转台########################################\n")
                mo = Motor()
                while True:
                    print('\n')
                    print('\n')
                    b=('################################测试转台################################\n'
                          '[0]：检查转台所有状态\n'
                          '[1]：转台寻零\n'
                          '[2]：转台以固定角度旋转测试[先40度旋转测试，后大角度旋转测试]\n'
                          '[3]：转台旋转测试到固定位置\n'
                          '[x]：返回上级测试项\n')

                    print(b)
                    file.write(b)
                    file.flush()
                    choose_number = input("选择功能：\n")
                    file.write(f"选择功能：{choose_number}\n")
                    file.flush()
                    motor_fail_message=""
                    motor_success_message = ""
                    test_fail=0
                    test_success=0

                    if choose_number == "0":
                        status=False
                        file.write("####################转台寻零######################\n")
                        file.flush()
                        print("转台寻零\n")
                        status=mo.cmd_find_zero()  # 转台寻零
                        if status==False:
                            print("转台寻零失败\n")
                            file.write("转台寻零失败\n")
                            file.flush()
                            test_fail+=1
                            motor_fail_message=motor_fail_message+"转台寻零失败\n"
                        else:
                            test_success +=1
                            motor_success_message=motor_success_message+"转台寻零成功\n"
                            print("转台寻零成功\n")
                            file.write("转台寻零成功\n")
                            file.flush()


                        print("以固定40度进行旋转测试\n")
                        file.write("################以固定40度进行旋转测试###################\n")
                        file.flush()
                        angles_list = [0,40, 80, 120, 160, 200, 240, 280, 320, 0,179,0,182,0,179,182,0]
                        for angles in angles_list:
                            status=mo.cmd_set_position(angles)  # 转台旋转测试到指定位置
                            if status==False:
                                print("转台旋转测试失败\n")
                                file.write(f"{angles}角度旋转测试失败\n")
                                file.flush()

                                test_fail +=1
                                motor_fail_message = motor_fail_message + "转台旋转测试失败\n"
                            else:
                                test_success +=1
                                print("转台固定角度旋转测试成功\n")
                                file.write(f"{angles}角度旋转测试成功\n")
                                file.flush()
                                motor_success_message = motor_success_message + "转台固定角度旋转测试成功\n"
                            time.sleep(2)

                        while True:
                            rotate_angle=input("请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                            if rotate_angle == 'x':
                                break
                            try:
                                rotate_angle = float(rotate_angle)
                                status=mo.cmd_set_position(rotate_angle)
                                if status==False:
                                    test_fail +=1
                                    motor_fail_message = motor_fail_message + "手动旋转测试失败\n"
                                    file.write(f"手动旋转{rotate_angle}测试失败\n")
                                    file.flush()
                                else:
                                    test_success+=1
                                    motor_success_message = motor_success_message +"手动旋转测试成功\n"
                                    file.write(f"手动旋转{rotate_angle}测试成功\n")
                                    file.flush()



                            except:
                                print("字符无法识别：请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                                file.write("字符无法识别：请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                                file.flush()


                    elif choose_number == "1":
                        status=mo.cmd_find_zero() #转台寻零
                        if status==False:
                            print("转台寻零失败")
                        else:
                            print("转台寻零成功")

                    elif choose_number == "2":
                        angles_list = [0,40, 80, 120, 160, 200, 240, 280, 320, 0,179,0,182,0,179,182,0]
                        for angles in angles_list:
                            status_signal=mo.cmd_set_position(angles)  # 转台旋转测试到指定位置
                            time.sleep(2)
                            if status_signal==False:
                                status=False
                        if status==False:
                            print("固定角度旋转失败\n")
                        else:
                            print("固定角度旋转成功\n")
                    elif choose_number == "3":
                        while True:
                            rotate_angle=input("请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                            if rotate_angle == 'x':
                                break
                            try:
                                rotate_angle = float(rotate_angle)
                                status=mo.cmd_set_position(rotate_angle)
                                if status==False:
                                    print("手动旋转测试失败\n")
                                else:
                                    print("手动旋转测试成功\n")
                            except:
                                print("字符无法识别：请输入要旋转测试的角度;若输入‘x’,则返回上级菜单;\n")
                    elif choose_number== 'x':
                        break

            elif choose_number0 == "2": # 测试小电机旋转测试
                file.write("#####################测试小电机旋转测试####################\n")
                file.flush()
                command0="echo 1 > /proc/rp_power/laser"
                file.write("echo 1 > /proc/rp_power/laser:打开激光")
                file.flush()
                process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True, text=True)
                process0.communicate()

                error_signal=False
                test_signal = 0
                mon = MinMotor1()
                limits = mon.detect_limit_switches()
                lefts_limits=limits['left_limit_angle']
                print(f"左限位角度:{lefts_limits}\n")
                right_limits=limits['right_limit_angle']
                print(f"右限位角度:{right_limits}\n")
                while not error_signal:
                    total_angle_limits=360-lefts_limits+right_limits
                    print(f"小电机左右限位的总角度：{total_angle_limits}\n")
                    if 270<total_angle_limits<280:
                        print("小电机限位角度正常\n")

                    else:
                        print("小电机左右限位角度异常，出现堵转\n")
                        error_signal =True
                        break

                    current_angle=mon.cmd_read_angle()
                    total_angle_limits=total_angle_limits+3
                    #转至左限位
                    print("小电机左限位转动中......")
                    mon.cmd_set_pos_ab(-total_angle_limits)
                    time.sleep(8)
                    after_angle=mon.cmd_read_angle()
                    print(f"往左转停角度{after_angle}\n")
                    if abs(lefts_limits-after_angle)<2:#左限位小电机旋转
                        #转至右限位
                        print("小电机右限位转动中......")
                        mon.cmd_set_pos_ab(total_angle_limits)
                        time.sleep(8)
                        after_angle=mon.cmd_read_angle()
                        print(f"往右转停角度{after_angle}\n")
                        if abs(right_limits-after_angle)<2:
                            print("小电机大角度旋转正常")
                        else:
                            print("右限位小电机堵转")
                            error_signal = True
                            break
                    else:
                        print("左限位小电机堵转")
                        error_signal = True
                        break
                    #小角度验证
                    total_rotated=0
                    max_rotation=300
                    test_angle=-5
                    #转至左限位
                    while abs(total_rotated)<max_rotation:
                        before_angle=mon.cmd_read_angle()
                        print(f"小角度旋转前当前角度:{before_angle}")
                        mon.cmd_set_pos_ab(test_angle)
                        time.sleep(1)
                        after_angle=mon.cmd_read_angle()
                        print(f"小角度旋转后当前角度:{after_angle}")
                        angle_diff = after_angle - before_angle

                        if angle_diff > 180:
                            angle_diff -= 360
                        elif angle_diff < -180:
                            angle_diff += 360
                        print(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}")
                        if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，触发限位，可能触发限位
                            if abs(after_angle - lefts_limits) <3 : #是否到达左限位
                                print("检测左限位已触发")
                                mon.cmd_set_pos_ab(-test_angle)
                                break
                            else:
                                error_signal=True
                                print("小电机堵转")
                                print(f"左限位角度:{lefts_limits}")
                                break

                        total_rotated += test_angle
                    if error_signal:
                        print("小电机堵转")
                        break
                    #转至右限位
                    total_rotated = 0
                    max_rotation = 300
                    test_angle = 5
                    # 转至右限位
                    while abs(total_rotated) < max_rotation:
                        before_angle = mon.cmd_read_angle()
                        print(f"小角度旋转前当前角度:{before_angle}")
                        mon.cmd_set_pos_ab(test_angle)
                        time.sleep(1)
                        after_angle = mon.cmd_read_angle()
                        print(f"小角度旋转后当前角度:{after_angle}")
                        angle_diff = after_angle - before_angle
                        if angle_diff > 180:
                            angle_diff -= 360
                        elif angle_diff < -180:
                            angle_diff += 360
                        print(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}")
                        if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，可能触发限位
                            if abs(after_angle - right_limits) < 3: #是否到达右限位
                                print("检测右限位已触发")
                                mon.cmd_set_pos_ab(-90)
                                break
                            else:
                                error_signal = True
                                print("小电机堵转")
                                print(f"右限位角度:{right_limits}")
                                break
                        total_rotated += test_angle
                    if error_signal:
                        print("小电机堵转")
                        break
                    else:
                        print("小电机旋转测试成功")
                        break

            elif choose_number0 == "3": #小电机,主要测试斑大小

                file.write("#####################激光旋转测试####################\n")
                file.flush()
                command0 = "echo 1 > /proc/rp_power/laser"
                file.write("echo 1 > /proc/rp_power/laser:打开激光")
                file.flush()
                process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True, text=True)
                process0.communicate()
                error_signal = False
                test_signal = 0
                mon = MinMotor1()
                limits = mon.detect_limit_switches()
                lefts_limits = limits['left_limit_angle']
                print(f"左限位角度:{lefts_limits}\n")
                file.write(f"左限位角度:{lefts_limits}\n")
                file.flush()
                right_limits = limits['right_limit_angle']
                file.write(f"右限位角度:{right_limits}\n")
                file.flush()
                print(f"右限位角度:{right_limits}\n")
                total_angle_limits = 360 - lefts_limits + right_limits
                while not error_signal:
                    # 小角度验证
                    total_rotated = 0
                    max_rotation = 300
                    test_angle = -2
                    # 转至左限位
                    while abs(total_rotated) < max_rotation:
                        before_angle = mon.cmd_read_angle()
                        print(f"小角度旋转前当前角度:{before_angle}")
                        file.write(f"小角度旋转前当前角度:{before_angle}\n")
                        file.flush()
                        mon.cmd_set_pos_ab(test_angle)
                        time.sleep(1)
                        after_angle = mon.cmd_read_angle()
                        print(f"小角度旋转后当前角度:{after_angle}")
                        file.write(f"小角度旋转后当前角度:{after_angle}\n")
                        file.flush()
                        angle_diff = after_angle - before_angle

                        if angle_diff > 180:
                            angle_diff -= 360
                        elif angle_diff < -180:
                            angle_diff += 360
                        print(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}")
                        file.flush()
                        if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，触发限位，可能触发限位
                            if abs(after_angle - lefts_limits) < 3:  # 是否到达左限位
                                print("检测左限位已触发")
                                file.write("检测左限位已触发\n")
                                file.flush()
                                mon.cmd_set_pos_ab(5)
                                time.sleep(2)
                                break
                            else:
                                error_signal = True
                                print("测试激光，小电机旋转堵转")
                                file.write("测试激光，小电机旋转堵转\n")
                                file.flush()
                                print(f"左限位角度:{lefts_limits}")
                                file.write(f"左限位角度:{lefts_limits}\n")
                                file.flush()

                                break

                        total_rotated += test_angle
                    if error_signal:
                        print("测试激光，小电机旋转堵转")
                        file.write("测试激光，小电机旋转堵转\n")
                        file.flush()
                        break
                    # 转至右限位
                    total_rotated = 0
                    max_rotation = 300
                    test_angle = 2
                    # 转至右限位
                    while abs(total_rotated) < max_rotation:
                        before_angle = mon.cmd_read_angle()
                        print(f"小角度旋转前当前角度:{before_angle}")
                        file.write(f"小角度旋转前当前角度:{before_angle}\n")
                        file.flush()
                        mon.cmd_set_pos_ab(test_angle)
                        time.sleep(1)
                        after_angle = mon.cmd_read_angle()
                        print(f"小角度旋转后当前角度:{after_angle}")
                        file.write(f"小角度旋转后当前角度:{after_angle}\n")
                        file.flush()
                        angle_diff = after_angle - before_angle
                        if angle_diff > 180:
                            angle_diff -= 360
                        elif angle_diff < -180:
                            angle_diff += 360
                        print(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}")
                        file.write(f"尝试旋转{abs(test_angle)}度，实际角度变化: {angle_diff}\n")
                        file.flush()


                        if abs(angle_diff) < abs(test_angle * 0.5):  # 变化小于80%，可能触发限位
                            if abs(after_angle - right_limits) < 3:  # 是否到达右限位
                                print("检测右限位已触发")
                                file.write("检测右限位已触发\n")
                                file.flush()
                                mon.cmd_set_pos_ab(-total_angle_limits/2)
                                break
                            else:
                                error_signal = True
                                print("测试激光，小电机旋转堵转\n")
                                print(f"右限位角度:{right_limits}\n")
                                file.write("测试激光，小电机旋转堵转\n")
                                file.write(f"右限位角度:{right_limits}\n")
                                file.flush()
                                break
                        total_rotated += test_angle
                    if error_signal:
                        print("测试激光，小电机旋转堵转")
                        file.write("测试激光，小电机旋转堵转\n")
                        file.flush()
                        break
                    else:
                        print("测试激光，小电机旋转完成")
                        file.write("测试激光，小电机旋转完成\n")
                        file.flush()
                        break


            elif choose_number0 == "4":  #测试雷达
                #URL = "http://192.168.1.201/pandar.cgi?action=get&object=device_info"
                # response = requests.get(URL)
                # result = response.json()
                #
                # result = requests.get(
                # url="http://192.168.1.201/pandar.cgi?action=get&object=lidar_data&key=lidar_calibration")
                # print(result.status_code)  # 请求状态
                # print(result.url)  # 请求url
                # need = result.json()['Body']['lidar_calibration']
                # print(need)  # 请求结果
                '''
                检查IP，配置PTP和回波模式
                :return:
                '''
                file.write("#####################雷达测试####################\n")
                file.flush()
                result=lidar_setting()
                if not result:
                    print("测试雷达失败")
                    file.write("测试雷达失败\n")
                    file.flush()
                else:
                    print("测试雷达成功")
                    file.write("测试雷达成功\n")
                    file.flush()




            elif choose_number0 == "5": #检查相机的拍照功能
                ###删除当前文件夹下的照片，再进行拍照，确定拍照功能

                file.write("###########相机拍照测试####################")

                count0 = 0
                for filename in os.listdir('/app'):
                    if filename.lower().endswith('.jpg'):
                        count0 += 1
                print(f"当前相机照片{count0}张\n")
                file.write(f"当前相机照片{count0}张\n")
                file.flush()
                # 开相机
                command0 = "echo 1 > /sys/control/power_camera1 && echo 1 > /sys/control/camera_power1" \
                           "&&echo 1 > /sys/control/power_camera2 && echo 1 > /sys/control/camera_power2"  # 检查开机时，相机是否已经连接
                process0 = subprocess.Popen(command0, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True, text=True)
                process0.communicate()
                print("等待相机启动\n")
                time.sleep(15)

                command1 = "lsusb | grep 'Sony' "  # 检查开机时，相机是否已经连接
                process1 = subprocess.Popen(command1, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True, text=True)
                stdout1 = process1.communicate()[0]
                print(f"相机返回：{stdout1}")
                file.write(f"相机连接详情：{stdout1}\n")
                file.flush()
                time.sleep(3)

                #with open("camera_number.txt", 'a', encoding='utf-8') as file:
                    #file.write(stdout1)
                sony_num = stdout1.count("Sony")
                print(f"sony出现次数：{sony_num}\n")

                if sony_num == 2:
                    print("相机全部开启\n")
                    file.write("相机全部开启\n")
                    file.flush()
                else:
                    print("存在相机开启失败\n")
                    file.write("存在相机开启失败\n")
                    file.flush()

                command2 = "/app/CrSDK/build/RemoteCli-test"  # 检查开机时，相机是否已经连接
                process2 = subprocess.Popen(command2, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                                            shell=True, text=True)
                process2.stdin.write("\n")
                process2.stdin.flush()

                # 立即继续执行，不等待进程结束
                time.sleep(20)

                count1 = 0
                for filename in os.listdir('/app'):
                    if filename.lower().endswith('.jpg'):
                        count1 += 1
                print(f"当前相机照片{count1}张\n")
                file.write(f"拍照后相机照片{count1}张\n")
                file.flush()
                if count1 == count0 + 2:
                    print("相机拍照功能正常\n")
                    file.write("相机拍照功能正常\n")
                    file.flush()

                else:
                    print("控制相机拍照失败，请再次进行测试\n")
                    file.write("控制相机拍照失败，请再次进行测试\n")

                    file.flush()

            elif choose_number0 =='x':
                file.write("已输入x，程序退出\n")
                file.flush()
                sys.exit()

            else:
                print('输入选项不正确')
                file.write('输入选项不正确\n')
                file.flush()


