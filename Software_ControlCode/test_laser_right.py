#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/10/20 15:31
# @Author  : bhb
# @Email   :
# @File    : testLareLight.py

import math
'''
测试找点
'''
#统一到全站仪坐标系，Z朝上，-x指向水准气泡（镜头），y指向电池仓
#tps_move_point=[0.0,-0.036,0.26678]#偏转的设计距离
tps_move_point=[0.0,0.0,0.0]
tps_move_angle=[83.832-90]#标定出来的角度与全站仪的偏角
print(math.atan((0.036-0.018)/2.6)/math.pi*180)#水平0.39°
print(math.atan((0.4238-0.26678)/2.6)/math.pi*180)#垂直3.456=============304  就是90度（朝X前方向）
#大转台角度=360-（90-83.832-0.39）则角度一致

def get_need_hv(global_point,angle0=0,):
    '''1.获取全站仪偏转角度(激光到全站仪的夹角，全站仪转动的夹角)
    2.获取激光笔的位置
    3.计算旋转角度
    '''
    #offset0=136.66/180*math.pi

    globalX,globalY,globalZ=global_point
    TPS_X, TPS_Y, TPS_Z = tps_move_point#激光笔的位置

    VectorX = globalX - TPS_X
    VectorY = globalY - TPS_Y
    VectorZ = globalZ - TPS_Z

    r = math.sqrt(VectorX * VectorX + VectorY * VectorY + VectorZ * VectorZ)
    tv = math.acos(VectorZ / r) # 竖直角弧度
    #thz = math.atan(VectorY / VectorX) # 水平角弧度
    thz = math.acos(VectorX / math.sqrt(VectorX * VectorX + VectorY * VectorY))
    #thz=thz
    if  VectorY < 0:
        thz = math.pi * 2 - thz
    return thz/math.pi*180,tv/math.pi*180

a=[-2.1703,-0.6138,-0.006]
#b=[0.8745,-1.6463,1.0783]
hz,v=get_need_hv(a)#全站仪坐标系下的角度
#hz,v=get_need_hv([0.7906,2.0005,0.2646])
offsetX=206.8-270
offsetY=-0.4
hz=hz+offsetX
if hz<0:
    hz=360+hz
print(hz+offsetY,v,0)