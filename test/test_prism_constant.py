import numpy as np
# import os
# import math
# import matplotlib.pyplot as plt

data_path=r"E:\2.1SE-T32\2.1采集数据\20241022棱镜球\2号球\2-2.txt"
total_station_datas=np.loadtxt(data_path,delimiter=',')[:,1:4]
num_rows, num_cols = total_station_datas.shape
num_row=int(num_rows/2)

total_station_datas0=total_station_datas[num_row:,:]  #棱镜球
total_station_datas1=total_station_datas[:num_row,:]  #墙面&

print(total_station_datas1)
total_station_datas1[:,-1]=0
num_rows, num_cols = total_station_datas1.shape
b=[0,0,0]
a=np.array(b)
distances1=[]
distances0=[]

for i in range(int((num_rows))):
    distance1=np.linalg.norm(total_station_datas1[i] - a)
    distances1.append(round(distance1,5))
    distance0=np.linalg.norm(total_station_datas0[i] - a)
    distances0.append(round(distance0,5))


print((sum(distances1)/len(distances1))-(sum(distances0)/len(distances0))-0.02006)  #0.02006是棱镜边缘到中心的位置

#distances1是墙面坐标，distances0是棱镜坐标

