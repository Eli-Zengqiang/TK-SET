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


def test_motor():
    mo = Motor()
    for i in range(340,0,-40):
        time.sleep(3)
        mo.cmd_set_position(i)
    time.sleep(3)
    mo.cmd_set_position(350)

# mo=Motor()
# for i in range(20):
#     mo.cmd_set_speed(2.94)
#     time.sleep(60)
#     for j in range(8):
#         mo.cmd_set_position(j*40)
#         time.sleep(3)
#     mo.cmd_set_speed(0)
#     time.sleep(10)

# send_cmd_bytes = [235, 17, 0, 0, 0, 0, 0, 0, 0, 190]
# send_cmd_bytes[2:6] = struct.pack('<f', 0.0)
# # 计算校验和
# num = 0
# for i in range(8):
#     num += send_cmd_bytes[i]
# send_cmd_bytes[8] = num % 256


if __name__ == "__main__":
    mo=Motor()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hfew:s:p:i:m:c:a:")
    except getopt.GetoptError:
        print('-f ,-w [filename], -s [set_speed],-p [set_position] -i [index]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-f find_zero,-w write_file, -s set_speed,-p set_position  -i index')
            sys.exit()
        elif opt =="-f":#转台找零
            mo.cmd_find_zero()
        elif opt =="-e":#让转台停止工作
            mo.cmd_stop_all()
        elif opt =="-w":#读取指定时间的角度，保存到默认文件
            mo.cmd_set_position(50.0)
            mo.cmd_set_speed(2.94)
            mo.start_read()
            mo.start_write()
            time.sleep(float(arg))
            mo.stop_read()
            mo.stop_write()
        elif opt == "-s":#按指定的速度转动
            mo.cmd_set_speed(float(arg))
        elif opt == "-p":#让转台转到指定位置
            mo.cmd_set_position(float(arg))
        elif opt == "-i":#设置转台自动累加的帧序号
            mo.cmd_set_index()
        elif opt=="-m":#设置转台的最大旋转速度
            mo.cmd_set_max_speed(float(arg))
            mo.cmd_save_para()
        elif opt=="-c":#设置转台的运动电流
            mo.cmd_set_current(float(arg))
            mo.cmd_save_para()
        elif opt=="-a":#设置转台的最大加速度最大减速度
            print("-a",arg)
            mo.cmd_set_max_addacc(float(arg))
            time.sleep(1)
            mo.cmd_set_max_racc(float(arg))
            time.sleep(1)
            mo.cmd_save_para()

