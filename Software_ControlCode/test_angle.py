#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/15 12:09
# @Author  : bhb
# @Email   : 
# @File    : test_angle.py
'''
检查角度突变的问题
'''
import math
import numpy as np
def check_angle_saltation(txt_path):
    with open(txt_path,"r") as f:
        lines=f.readlines()
        for i in range(1,len(lines)):
            angle_0=float((lines[i-1]).strip().split(',')[1])
            angle_1=float((lines[i]).strip().split(',')[1])
            if math.fabs(angle_0-angle_1)>0.05:
                print(f"第{i}行存在大于0.05的突变")

#check_angle_saltation(r"E:\Code\GitSource\linuxCameraPad201\20230815\2_angle.txt")



def change_angles(txt_path=r"C:\Users\bhb\Desktop\t1.txt",out_path=r"C:\Users\bhb\Desktop\t1_.txt"):
    new_lines=[]
    with open(txt_path) as f:
        lines=f.readlines()
        first_i=0
        first_t=0
        for i,line in enumerate(lines):
            _s,_p,_i,_t=line.split()
            new_t = np.float64(_t[:10] + "." + _t[10:17])
            _i=int(_i)
            if i == 0:
                first_i=_i
                first_t=new_t
            else:
                if _i<first_i:
                    _i+=65535#过了一圈了
                new_t+=(_i-first_i)*0.001
            new_lines.append(f"{_s} {_p} {_i} {new_t}\n")
    with open(out_path,"w") as f:
        f.writelines(new_lines)


change_angles(r"E:\Code\GitSource\linuxCameraPad201\20230829_angles.txt",r"E:\Code\GitSource\linuxCameraPad201\20230829_angles1.txt")
# print(math.atan(0.001/160)/math.pi*180)
# _data=np.array([[0.000358*2,0.318,0.245],
# [0.000358*32,0.305,0.256],
# [0.000358*38,0.302,0.251],
# [0.000358*100,0.288,0.263],
# [0.000358*120,0.281,0.259]])
#
# # _data=np.array([[0.000358*-15,3.067,0.534],
# # [0.000358*20,3.075,0.538],
# # [0.000358*50,3.077,0.551],
# # [0.000358*121,3.077,0.572]])
# for i in range(1,len(_data)):
#     a = _data[i, :] - _data[i - 1, :]
#     print(a)


