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
        self.left_limit_angle = None
        self.right_limit_angle = None

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

    def cmd_set_pos(self, input_angle, delay_time=60):
        '''
        PID转动到目标绝对角度，确保在可行区域内转动
        :param input_angle: 目标绝对角度(0-360)
        :param delay_time: 超时时间(秒)
        :return: True/False
        '''
        # 1. 检查限位角度是否已设置
        if self.left_limit_angle is None or self.right_limit_angle is None:
            print("未设置左右限位角度，无法执行转动")
            return False

        # 2. 将输入角度归一化到[0, 360)
        input_angle = input_angle % 360

        # 3. 获取当前角度并归一化
        start_angle = self.cmd_read_angle()
        if start_angle < 0:
            start_angle += 360
        start_angle = start_angle % 360

        print(f"-----------输入的转动角度：{input_angle}")
        print(f"当前角度: {start_angle}")

        # 4. 检查目标角度是否都在可行区域内
        if not self._is_angle_in_range(input_angle):
            print(f"目标角度{input_angle}不在可行区域内！")
            return False

        # 5. 计算两个可能的转动方向（顺时针和逆时针）
        # 顺时针角度差
        cw_diff = (input_angle - start_angle) % 360
        # 逆时针角度差（负值）
        ccw_diff = cw_diff - 360

        # 6. 检查两个方向是否都穿过禁止区域
        cw_path_valid = self._check_path_valid(start_angle, input_angle, True)
        ccw_path_valid = self._check_path_valid(start_angle, input_angle, False)

        print(f"顺时针路径有效: {cw_path_valid}, 逆时针路径有效: {ccw_path_valid}")

        # 7. 选择可行的转动方向
        if not self._is_angle_in_range(start_angle):
            print(f"起始角度{start_angle}不在可行区域内！")
            step_angle = cw_diff if abs(cw_diff) <= abs(ccw_diff) else ccw_diff
        else:
            if not cw_path_valid and not ccw_path_valid:
                print("两个方向都穿过禁止区域，无法到达目标位置！")
                return False
            elif cw_path_valid and ccw_path_valid:
                # 两个方向都可行，选择最短路径
                step_angle = cw_diff if abs(cw_diff) <= abs(ccw_diff) else ccw_diff
            elif cw_path_valid:
                step_angle = cw_diff
            else:
                step_angle = ccw_diff

        print(f"-----------选择的转动角度：{step_angle}")

        # 8. 执行PID控制循环
        protect_num = 0
        same_angle_num = 0
        last_angle = start_angle
        start_time = time.time()

        # 首次转动
        if not self.cmd_set_pos_ab(step_angle):
            print("首次转动触发限位，解除保护...")
            self.cmd_reset_protect()
            protect_num += 1

        while time.time() - start_time < delay_time:
            if protect_num > 1:
                print("-----------多次触发限位保护，检查输入参数！！！！！！！！！！")
                break
            if same_angle_num > 3:
                print("多次转动后角度无变化，请返回上层目录用【解除堵转（含重启小电机）】处理")
                break

            time.sleep(1)
            current_angle = self.cmd_read_angle()

            # 归一化当前角度
            if current_angle < 0:
                current_angle += 360
            current_angle = current_angle % 360

            print(f"当前角度:{current_angle}")

            # 检查是否移动到禁止区域
            # if not self._is_angle_in_range(current_angle):
            #     print(f"警告：当前角度{current_angle}不在可行区域内！")
            #     self.cmd_reset_protect()
            #     protect_num += 1
            #     continue

            # 检查角度是否变化
            if math.fabs(last_angle - current_angle) < 0.1:
                same_angle_num += 1

            last_angle = current_angle

            # 检查是否到达目标
            diff = (input_angle - current_angle) % 360
            if diff > 180:
                diff -= 360

            if math.fabs(diff) < 0.1:
                print("-----------转动到指定角度，转动完成")
                return True

            # 重新计算步进角度，考虑避免禁止区域
            step_angle = self._calculate_safe_step(current_angle, input_angle)
            if step_angle is None:
                print("无法找到安全的转动路径！")
                return False

            # 控制旋转
            time.sleep(0.5)
            print(f"转动角度:{step_angle}")

            if not self.cmd_set_pos_ab(step_angle):
                print("触发限位，解除保护...")
                self.cmd_reset_protect()
                protect_num += 1

        # 超时处理
        print("-----------规定时间未转动到指定位置，转动失败！！！！！！！！！！")
        print("-------------------耗时", time.time() - start_time)
        return False

    def _is_angle_in_range(self, angle):
        """检查角度是否在可行区域内"""
        left = self.left_limit_angle % 360
        right = self.right_limit_angle % 360

        if left <= right:
            # 正常情况：左限位 <= 右限位，可行区域是 [left, right]
            return left <= angle <= right
        else:
            # 跨越0点：左限位 > 右限位，可行区域是 [left, 360) ∪ [0, right]
            return left <= angle <= 360 or 0 <= angle <= right

    def _check_path_valid(self, start_angle, end_angle, clockwise):
        """
        检查转动路径是否有效（不穿过禁止区域）
        :param start_angle: 起始角度
        :param end_angle: 结束角度
        :param clockwise: True=顺时针，False=逆时针
        :return: True=路径有效
        """
        if clockwise:
            # 顺时针转动
            if start_angle <= end_angle:
                # 路径区间：[start_angle, end_angle]
                path_start = start_angle
                path_end = end_angle
            else:
                # 跨越0点，路径区间：[start_angle, 360) ∪ [0, end_angle]
                # 需要检查两个区间
                return (self._check_single_segment(start_angle, 360, clockwise) and
                        self._check_single_segment(0, end_angle, clockwise))
        else:
            # 逆时针转动
            if start_angle >= end_angle:
                # 路径区间：[end_angle, start_angle]
                path_start = end_angle
                path_end = start_angle
            else:
                # 跨越0点，路径区间：[0, start_angle] ∪ [end_angle, 360)
                return (self._check_single_segment(0, start_angle, clockwise) and
                        self._check_single_segment(end_angle, 360, clockwise))

        # 检查单个路径区间
        return self._check_single_segment(path_start, path_end, clockwise)

    def _check_single_segment(self, start_angle, end_angle, clockwise):
        """
        检查单个连续的路径区间是否有效
        """
        # 获取区间内的采样点进行检查（每度检查一个点）
        step = 1.0  # 每度采样一个点
        if start_angle <= end_angle:
            # 正常区间
            current_angle = start_angle
            while current_angle <= end_angle:
                if not self._is_angle_in_range(current_angle):
                    return False
                current_angle += step
        else:
            # 跨越0点的区间，需要检查两段
            # 第一段：[start_angle, 360)
            current_angle = start_angle
            while current_angle < 360:
                if not self._is_angle_in_range(current_angle):
                    return False
                current_angle += step

            # 第二段：[0, end_angle]
            current_angle = 0
            while current_angle <= end_angle:
                if not self._is_angle_in_range(current_angle):
                    return False
                current_angle += step

        return True

    def _calculate_safe_step(self, current_angle, target_angle):
        """
        计算安全的步进角度，确保不穿过禁止区域
        """
        # 计算两个方向
        cw_diff = (target_angle - current_angle) % 360
        ccw_diff = cw_diff - 360

        # 检查两个方向的有效性
        cw_valid = self._check_path_valid(current_angle, target_angle, True)
        ccw_valid = self._check_path_valid(current_angle, target_angle, False)
        if not self._is_angle_in_range(current_angle):
            return cw_diff if abs(cw_diff) <= abs(ccw_diff) else ccw_diff
        else:
            if cw_valid and ccw_valid:
                # 两个方向都可行，选择最短路径
                return cw_diff if abs(cw_diff) <= abs(ccw_diff) else ccw_diff
            elif cw_valid:
                return cw_diff
            elif ccw_valid:
                return ccw_diff
            else:
                return None


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


    def cmd_set_work_mode(self,is_open=True,delay_time=10):
        '''
        设置工作模式 开环/闭环
        :return:
        '''
        self.com.flushInput()
        if is_open:
            self.com.write([0x01, 0x46, 0x69, 0x01, 0x01, 0x6b])
        else:
            self.com.write([0x01, 0x46, 0x69, 0x01, 0x02, 0x6b])#闭环的指令
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
                self.left_limit_angle = after_angle
                break

            total_rotated += test_angle

            # 如果返回错误状态，说明触发限位
            if not result:
                print("左限位触发")
                left_limit_reached = True
                self.left_limit_angle = after_angle
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
                self.right_limit_angle = after_angle
                break

            total_rotated += test_angle

            # 如果返回错误状态，说明触发限位
            if not result:
                print("右限位触发")
                right_limit_reached = True
                self.right_limit_angle = after_angle
                # 解除保护
                self.cmd_reset_protect()
                break

        # 回到中间位置
        print("返回中间位置...")

        # 再从起始点回到中间位置
        current_angle = self.cmd_read_angle()
        # 计算中间角度，考虑跨越0度的情况
        if self.left_limit_angle is not None and self.right_limit_angle is not None:
            total_angle=(360-self.left_limit_angle)+self.right_limit_angle#总的行程
            angle_to_middle=-total_angle/2
            middle_angle = self.right_limit_angle+angle_to_middle
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
            "left_limit_angle": self.left_limit_angle,
            "right_limit_angle": self.right_limit_angle,
            "initial_angle": initial_angle,
            "final_angle": final_angle
        }

        print("限位检测结果:")
        print(f"  初始位置: {initial_angle}")
        print(f"  左限位: {'触发' if left_limit_reached else '未触发'}")
        if self.left_limit_angle is not None:
            print(f"    触发角度: {self.left_limit_angle}")
        print(f"  右限位: {'触发' if right_limit_reached else '未触发'}")
        if self.right_limit_angle is not None:
            print(f"    触发角度: {self.right_limit_angle}")
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

