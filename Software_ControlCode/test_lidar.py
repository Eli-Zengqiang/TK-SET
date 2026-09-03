#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/15 17:05
# @Author  : bhb
# @Email   : 
# @File    : test_lidar.py
import math
import numpy as np

from Lidar_XT import Lidar_XT
import os

def check_angle_saltation(txt_path):
    with open(txt_path,"r") as f:
        lines=f.readlines()
        print("一共有",len(lines),"个点")
        print("开始时间:",np.float64((lines[0]).strip().split(' ')[4]))
        print("结束时间:", np.float64((lines[-1]).strip().split(' ')[4]))
        current_txt_id=1
        for i in range(16,len(lines)):
            time_0=np.float64((lines[i-16]).strip().split(' ')[4])
            time_1=np.float64((lines[i]).strip().split(' ')[4])
            if math.fabs(time_1-time_0)>0.000003*2:
                print(f"第{i}行存在大于0.000003*2的突变,减少了{round(time_1-time_0,6)}s")
                _x,_y,_z,_i,_t,select_id=lines[i].strip().split()
                #打印出上下
                top_points=lines[i-16*100:i]
                bottom_points = lines[i:i + 16 * 100]
                #print(lines[i-16:i+16])
                start_time=np.float64(0)
                with open(f"{current_txt_id}.txt","w") as f:
                    print(current_txt_id)
                    for _index, line in enumerate(top_points):
                        _x,_y,_z,_i,_t,_id = line.strip().split()
                        _t=np.float64(_t)
                        if _index==0:
                            start_time=_t
                        if _id!=select_id:
                            continue
                        wline=f"{_x} {_y} {_z} {_i} {_t-start_time} {_id} 255 0 0\n"
                        #print(wline)
                        f.write(wline)
                    for line in bottom_points:
                        _x, _y, _z, _i, _t, _id = line.strip().split()
                        _t = np.float64(_t)
                        if _id != select_id:
                            continue
                        wline=f"{_x} {_y} {_z} {_i} {_t-start_time} {_id} 0 255 0\n"
                        f.write(wline)
                #break
                current_txt_id+=1


#check_angle_saltation(r"E:\Code\GitSource\HesaiLidar_General_SDK-win\build\Release\txt\0.txt")


def check_0(txt_path,write_txt=False):
    with open(txt_path, "r") as f:
        lines = f.readlines()
        current_txt_id = 1
        for i in range(16, len(lines)):
            time_0 = np.float64((lines[i - 16]).strip().split(' ')[6])
            time_1 = np.float64((lines[i]).strip().split(' ')[6])
            if math.fabs(time_1 - time_0) > 0.0005:
                print(f"第{i}行存在大于0.0005的突变,间隔了{time_1 - time_0}s")
                print(lines[i])
                _x, _y, _z, _i, _c,_id,_t = lines[i].strip().split()
                top_points = lines[i - 16 * 100:i]
                bottom_points = lines[i:i + 16 * 100]
                start_time = np.float64(0)
                if write_txt:
                    with open(f"{current_txt_id}.txt", "w") as f:
                        print(current_txt_id)
                        for _index, line in enumerate(top_points):
                            _x, _y, _z, _i, _c, select_id,_t = line.strip().split()
                            if _id != select_id:
                                continue
                            wline = f"{_x} {_y} {_z} {_i} {_t} {_id} 255 0 0\n"
                            # print(wline)
                            f.write(wline)
                        for line in bottom_points:
                            _x, _y, _z, _i, _c, select_id,_t = line.strip().split()
                            if _id != select_id:
                                continue
                            wline = f"{_x} {_y} {_z} {_i} {_t} {_id} 0 255 0\n"
                            f.write(wline)
                # break
                current_txt_id += 1


#check_0(r"E:\Code\GitSource\linuxCameraPad201\t2.txt")

def check_point_num(txt_path):
    with open(txt_path,"r") as f:
        lines=f.readlines()
        print("一共有",len(lines),"个点")
        print("开始时间:",np.float64((lines[0]).strip().split(' ')[4]))
        print("结束时间:", np.float64((lines[-1]).strip().split(' ')[4]))
        print(len(lines)/(np.float64((lines[-1]).strip().split(' ')[4])-np.float64((lines[0]).strip().split(' ')[4])))
        current_time_int=0
        current_point_num=0
        for i in range(len(lines)):
            if (lines[i]).strip().split(' ')[-1]!='0':
                continue
            current_time_int_=np.int(np.float64((lines[i]).strip().split(' ')[4]))
            if current_time_int!=current_time_int_:
                print(current_time_int_, current_point_num)
                current_time_int=current_time_int_
                current_point_num=0

            else:
                current_point_num+=1

#check_point_num(r"C:\Users\ZHXR\Desktop\2.1临时数据\out\0.txt")


def read_lidar_bin(path=r"E:\Code\GitSource\linuxCameraPad201\t1.txt",out_path=r"E:\Code\GitSource\linuxCameraPad201\t2.txt",need_add_8=True):
    '''

    :param path:
    :return:
    '''
    xt=Lidar_XT()
    _lines=[]
    with open(path,"rb") as f:
        filesize = os.stat(path).st_size
        print(filesize)
        curren_size=0
        while curren_size<filesize:
            data=f.read(568)
            _str=xt.prash_data(data,need_add_8)
            _lines.extend(_str["points"])
            curren_size+=568
            #print(_str)
    # new_lines=[]
    # for line in _lines:
    #     x,y,z=line.split()[0:3]
    #     new_lines.append(f"{x},{y},{z},")
    with open(out_path,"w") as f:
        f.writelines(_lines)



read_lidar_bin(r"C:\Users\ZHXR\Desktop\2.1data\20240201\2024020103\0_0.bin",r"C:\Users\ZHXR\Desktop\2.1data\20240201\2024020103\0_0.txt",True)
read_lidar_bin(r"C:\Users\ZHXR\Desktop\2.1data\20240201\2024020103\180_0.bin",r"C:\Users\ZHXR\Desktop\2.1data\20240201\2024020103\180_0.txt",True)
read_lidar_bin(r"C:\Users\ZHXR\Desktop\2.1data\20240201\2024020103\1_0.bin",r"C:\Users\ZHXR\Desktop\2.1data\20240201\2024020103\1_0.txt",True)
read_lidar_bin(r"C:\Users\ZHXR\Desktop\2.1data\20240201\2024020103\1_180.bin",r"C:\Users\ZHXR\Desktop\2.1data\20240201\2024020103\1_180.txt",True)
# import os
# dir=r"C:\Users\bhb\Desktop\1\22"
# for path in os.listdir(dir):
#     if path[-4:]==".csv":
#         with open(f"{dir}\\{path}") as f:
#             lines=f.readlines()
#             print(len(lines))


def point2area_distance(normal,center, point4):
    """
    :param point1:数据框的行切片，三维
    :param point2:
    :param point3:
    :param point4:
    :return:点到面的距离
    """
    Ax, By, Cz=normal
    D=-(Ax*center[0]+By*center[1]+Cz*center[2])
    mod_d = Ax * point4[0] + By * point4[1] + Cz * point4[2] + D
    mod_area = np.sqrt(np.sum(np.square([Ax, By, Cz])))
    d = abs(mod_d) / mod_area
    return d
#dis=point2area_distance([0.04776,0.013294,0.99877],[-0.260477,0.0418097,0.114147],[0.949165,0.83476,0.336344])
#print(dis)