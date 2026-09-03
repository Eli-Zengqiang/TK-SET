#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/10/31 14:39
# @Author  : bhb
# @Email   : 
# @File    : test_motor_txt.py

import numpy as np
import os

from test_lidar import read_lidar_bin

def test_lidar_txt(txt_path=r"C:\Users\ZHXR\Desktop\2.1data\2023-12-21-13-51-37\2023-12-21-13-51-3701\0.tkz"):  #r"C:\Users\bhb\Desktop\202310306.000--360\txt\0.tkz"
    '''

    :return:
    '''
    angles=[]
    times=[]
    with open(txt_path,"r",encoding='utf-8') as f:
        lines=f.readlines()
        for line in lines:
            #line_str=line.decode("utf-8")
            time=line.strip().split()[-2]
            #angles.append(np.float64(angle))
            times.append(np.float64(time))

    dif_record=(1/5/4000)*2
    for i in range(1,len(times)):
        if times[i]-times[i-1]>dif_record:
            num0=(times[i]-times[i-1])
            print(i,"时间相差",num0,"S")
    return angles,times
dir=r"C:\Users\ZHXR\Desktop\2.1data\2023-12-21-13-51-37\2023-12-21-13-51-3701"
for path in os.listdir(dir):
    #print(path)
    if path[-3:] == 'tkz':
        full_path=os.path.join(dir,path)
    else:
        continue
    #print(full_path)
    read_lidar_bin(full_path,full_path.replace(".tkz",".txt"))
    #test_lidar_txt(full_path)