
import numpy as np


import prism_ball.read_station_file as rf

total_points_file=r"E:\2.1SE-T32\2.1采集数据\20241112验证10-20m\全站仪打点\全站仪打点.txt"

a = np.array([2.255400,31.838900,2.539800])

datas=rf.read_station_points(total_points_file)
length=len(datas)/2
distances=[]
for id in range(int(length)):
    c=np.array(datas[2*id],dtype=float)
    b=np.array(datas[2*id+1],dtype=float)
    d=(b+c)/2
    distance = np.linalg.norm(a - b)

    distances.append(round(distance))


print(distances)



#i =(h+g)/2





print(f"距离1:{distance}")



