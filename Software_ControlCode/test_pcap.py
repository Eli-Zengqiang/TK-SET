#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/8/24 18:21
# @Author  : bhb
# @Email   : 
# @File    : test_pcap.py

# coding=utf-8


from scapy.all import *
from Lidar_XT import Lidar_XT




#file=rdpcap(r"C:\Users\bhb\Desktop\3.pcap")
def change_pcap2txt(pcap_path,txt_path):
    file=rdpcap(pcap_path)
    xt=Lidar_XT()
    id=0
    last_data_time=0
    with open(txt_path,"w") as f:
        for data in file:
            if "UDP" not in data:
                continue
            get_data=data["Raw"].load
            if len(get_data)!=568:
                continue
            if data.time-last_data_time>0.001:#1ms
                print(id,data.time-last_data_time)
            last_data_time=data.time
            prashed_data=xt.prash_data(get_data)
            if id%1000==0:
                print(id,prashed_data)
            id+=1
            f.writelines(prashed_data["points"])
#change_pcap2txt(r"test.txt","t4.txt")

import numpy as np
import cv2
#import pandas as pd
# angle=np.full((10000,16),np.nan)
# angle[0]=[0,2,4,6,8,10,12,14,180,182,184,186,188,190,192,194]
# hz=5
# max_angle=np.full((10000,2),np.nan)
# for j,angle_per_sec in enumerate(np.arange(2.0,10.0,0.01)):
#     for i in range(180/angle_per_sec*hz):
#         angle[i+1]=angle[0]+i*angle_per_sec/5
#         angle[i+1][angle[i+1]>360]=angle[i+1][angle[i+1]>360]-360
#     angle_1d=np.sort(angle[np.where(~np.isnan(angle))])
#     max_angle[j,0]=angle_per_sec
#     max_angle[j,1]=max(angle_1d[1:-1]-angle_1d[0:-2])
# df_max_angle=pd.DataFrame(max_angle)
# df_max_angle.sort_values(by=1,inplace=True)
# print(df_max_angle)

def computer_speed(set_speed,line_num=16):
    '''

    :param set_speed:
    :param line_num:
    :return:
    '''
    current_angles=np.array([i*2 for i in range(line_num)])
    current_angles_array=[]
    current_angles_array.append(current_angles)

    #计算每0.2s的位置,填满180°
    for i in range(1,100000):#算1000*0.2=200s
        current_angles_array.append(current_angles_array[0]+0.2*set_speed*i)
        if current_angles_array[-1][0]>360:
            break

    #平摊开，看下角度间隔
    current_angles_array=np.array(current_angles_array)

    angles =current_angles_array.flatten()
    angles=np.sort(angles)
    f=np.gradient(angles)
    print("mean:",f.mean(),"max:",f.max(),"min:",f.min())
    #print(current_angles_array)
    img=np.zeros((20,3600),dtype=np.uint8)
    for angle in angles:
        angle_=int(angle*10)
        cv2.line(img,(angle_,0),(angle_,20),(255,255,255),1)
    cv2.imwrite(f"{set_speed}.png",img)
    ratio=img.sum()/3600/20/255
    #print(ratio)
    return ratio

# for i in range(515,537,1):
#     ratio=computer_speed(i/100)
#     if ratio>0.94:
#         print("-------------------",ratio,i/100)
#computer_speed(5)


