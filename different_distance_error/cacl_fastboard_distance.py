import numpy as np
import math

def cacl_move_distance(distance=30):

    move_distance=[]
    third_distance=[]
    angles=[0.02,0.05,0.07,0.1,0.2]
    for angle in angles:
        move_distance.append((angle,round(distance*math.tan(angle/180*math.pi),4)))
        third_distance.append((angle,round(distance/math.cos(angle/180*math.pi),4)))
    print(f"计算对应角度，左右平移的距离(角度°，距离m)：{move_distance}")
    print(f"计算对应角度，斜边的距离距离(角度°，距离m)：{third_distance}")

def cacl_move_angles(distance=30):

    move_distances=[0.002,0.005,0.001,0.01,0.02]
    angles=[]
    for move_distance in move_distances :
        angles.append((move_distance,round((math.atan(move_distance/distance))/math.pi*180,4)))
    print(f"计算左右平移的对应角度(距离m,角度°)：{angles}")

if __name__=="__main__":
    distance = 4.7

    #cacl_move_distance(distance)
    cacl_move_angles(distance)


