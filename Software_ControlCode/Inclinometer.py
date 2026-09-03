#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/8 15:18
# @Author  : bhb
# @Email   : 
# @File    : inclinometer.py

# !/usr/bin/python
# -*- coding: UTF-8 -*-
# 倾角仪读数
import sys, getopt
import serial
import time
from utils import x2bcd


class Inclinometer:

    def __init__(self,com_name="/dev/ttyS4",bound_raito=9600):
        self.com = serial.Serial(com_name, bound_raito)
        self.current_inc_x=0.0#倾角仪X
        self.current_inc_y=0.0#倾角仪Y

    def __del__(self):
        if self.com.is_open:
            self.com.close()

    def _get_inc(self):#获取倾角仪数据
        get_state=False
        self.com.write([0x68,0x04,0x00,0x04,0x08])  #写入命令读取倾角仪X、Y角度
        time.sleep(0.1)
        start_time=time.time()
        while True:
            if self.com.in_waiting:
                data = self.com.read(self.com.in_waiting)#获取串口返回数据
                # data=b'h\x10\x00\x84\x10\x01b\x00\x00\x00"@\x00\x00\x00\x00i'  倾角仪角度
                if data[0] == 0x68 and data[3] == 0x84:
                    self.current_inc_x = x2bcd(data[5]) + x2bcd(data[6]) * 0.01 + x2bcd(data[7]) * 0.0001
                    if data[4] == 0x10:
                        self.current_inc_x *= -1
                    self.current_inc_y = x2bcd(data[9]) + x2bcd(data[10]) * 0.01 + x2bcd(data[11]) * 0.0001
                    if data[8] == 0x10:
                        self.current_inc_y *= -1
                    print(self.current_inc_x, self.current_inc_y)
                    get_state=True
                break
            if time.time()-start_time>2:
                print("倾角仪读数超时")
                break
        return get_state

    def save_inc(self,txt_path):
        if self._get_inc():
            try:
                with open(txt_path, "w") as f:
                    f.write(f"{self.current_inc_x},{self.current_inc_y}")
            except Exception as e:
                print("文件写入失败：",e)
                return False
        else:
            print("获取倾角仪数据失败")
            return False
        return True

    def _get_abs_zero(self):    #
        print("_get_abs_zero")
        self.com.write([0x68,0x04,0x00,0x0D,0x11]) #寻找绝对零位
        time.sleep(1)
        start_time=time.time()
        while True:
            if self.com.in_waiting:
                data = self.com.read(self.com.in_waiting)
                # data=b'h\x10\x00\x84\x10\x01b\x00\x00\x00"@\x00\x00\x00\x00i'
                print(data)
                if data[0] == 0x68 and data[3] == 0x8D:
                    if data[4] == 0x00:
                        print("当前采用的绝对零点")
                    elif data[4] == 0xFF:
                        print("当前采用的相对零点")
                break
            if time.time()-start_time>2:
                print("倾角仪读数超时")
                break



if __name__ == "__main__":
    outputfile=""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:z:", ["ofile="])    #sys.argv是一个列表，argv[0] 是 被调用的脚本文件名或全路径。argv[1：] 是后接参数值
        # getopt.getopt(args,shortopts,longopts)，如getopt.getopt(args,“h”,“help”)即h：-h，help：--help，此时外部输入-h和--help代表同样含义
        # 如传入的参数为： -z 0，则opts = [('-z','0')],args=[]，该参数为空，但必不可少
        #ho:,说明h是无参数值，o：说明o后面需要接参数值
    except getopt.GetoptError:
        print(' -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-o <outputfile>')
            sys.exit()
        elif opt in ("-o", "--ofile"):
            outputfile = arg
            if outputfile != "":#存数据
                inc = Inclinometer()
                inc.save_inc(outputfile)
        elif opt in ("-z"):#获取是绝对0位还是相对0位。当opts = [('-z','0')]
            inc = Inclinometer()
            inc._get_abs_zero()

