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
        self.com.write([0x01,0x46,0x69,0x01,0x01,0x6b])
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
        limit_signal_0=False

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
                limit_signal_0=True
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

        limit_signal_0 = False
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
                limit_signal_0 = True
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
        print("返回中间位置...")

        # 再从起始点回到中间位置
        current_angle = self.cmd_read_angle()
        # 计算中间角度，考虑跨越0度的情况
        if left_limit_angle is not None and right_limit_angle is not None:
            if limit_signal_0:  #此时过0
                total_angle=(360-left_limit_angle)+right_limit_angle#总的行程
                angle_to_middle=-total_angle/2
                middle_angle = right_limit_angle+angle_to_middle
                if middle_angle<0:
                    middle_angle+=360
            else: #此时未过0
                total_angle=abs(left_limit_angle-right_limit_angle)#总的行程
                angle_to_middle=-total_angle/2
                middle_angle = right_limit_angle+angle_to_middle
                if middle_angle<0:
                    middle_angle+=360
        else:
            # 如果没有检测到限位，则使用初始位置作为中间位置
            middle_angle = initial_angle
            angle_to_middle = middle_angle - current_angle

        print(f"从当前位置 {current_angle} 度转到中间位置 {middle_angle} 度，需要转动 {angle_to_middle} 度")
        self.cmd_set_pos_ab(angle_to_middle)
        time.sleep(3)

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
        if abs(total_angle -270)> 15:
            print("查找限位过程中，出现堵转")
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



if __name__ == "__main__":
    mo=MinMotor()
    #mo.cmd_set_open_current(1000,True)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hap:f:rt:zdl")
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
        elif opt =="-l":#设置零度
            mo.detect_limit_switches()

