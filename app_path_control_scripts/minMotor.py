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


if __name__ == "__main__":
    mo=MinMotor()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hap:f:rt:zd")
    except getopt.GetoptError:
        print('-a ,-p [set_position_ab],-f [xf number]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-a ,-p [set_position_ab],-f [xf number]')
            sys.exit()
        elif opt =="-a":#获取编码器角度
            mo.cmd_read_angle()
        elif opt =="-p":#转动绝对角度+简易PID
            angle=float(arg)
            mo.cmd_set_pos(angle)
        elif opt =="-f":#设置细分
            xf=int(arg)
            mo.cmd_set_xf(xf)
        elif opt =="-r":#恢复
            mo.cmd_reset_protect()
        elif opt =="-t":#相对位置转动
            angle = float(arg)
            mo.cmd_set_pos_ab(angle)
        elif opt =="-z":#设置零度
            mo.cmd_set_zero()
        elif opt =="-d":#设置零度
            mo.cmd_read_angle_current()

