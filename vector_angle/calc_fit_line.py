from PyQt5.QtCore import Qt, QThread, pyqtSignal
import skspatial.objects as sko
import numpy as np
import open3d as o3d
import os
import time

import numpy as np
import math
import matplotlib.pyplot as plt

txt_path1=r"E:\2.1SE-T32\2.1采集数据\20240801会堂棱镜杆\2024-08-01_10-27-21未搬站\未搬站1.txt"
txt_path2=r"E:\2.1SE-T32\2.1采集数据\20240801会堂棱镜杆\2024-08-01_10-48-38重装4\重装4.txt"
txt_path3=r"E:\2.1SE-T32\2.1采集数据\20240717棱镜杆\未搬站3.txt"
txt_path4=r"E:\2.1SE-T32\2.1采集数据\20240717棱镜杆\重装4_1.txt"
txt_path5=r"E:\2.1SE-T32\2.1采集数据\20240717棱镜杆\重装4_2.txt"
txt_path6=r"E:\2.1SE-T32\2.1采集数据\20240717棱镜杆\重装4_3.txt"
points_group1 = np.loadtxt(txt_path1)[:, 0:2]
points_group2 = np.loadtxt(txt_path2)[:, 0:2]
points_group3 = np.loadtxt(txt_path3)[:, 0:2]
points_group4 = np.loadtxt(txt_path4)[:, 0:2]
points_group5 = np.loadtxt(txt_path5)[:, 0:2]
points_group6 = np.loadtxt(txt_path6)[:, 0:2]
# points_group1= np.concatenate((points_group1, points_group2,points_group3), axis=0)
# points_group2= np.concatenate((points_group4, points_group5,points_group6), axis=0)
# points_group1= np.concatenate((points_group1,points_group3), axis=0)
# points_group2= np.concatenate((points_group4,points_group6), axis=0)
#print(points_PC)
#
# # 示例数据点，这里我们手动分成两组
#points_group1 = np.array([[1, 2], [2, 4], [3, 5]])
#print(points_group1)
#points_group2 = np.array([[4, 3], [5, 2], [6, 1]])

# 对每组点分别进行线性拟合
slope1, intercept1 = np.polyfit(points_group1[:, 0], points_group1[:, 1], 1)
slope2, intercept2 = np.polyfit(points_group2[:, 0], points_group2[:, 1], 1)

# 计算两条直线的夹角（注意：这里的角度计算假设了直线的倾斜角在-90到90度之间）
# 如果斜率不存在（即直线垂直于x轴），需要特殊处理
if slope1 == 0 or slope2 == 0:
    angle = 90  # 其中一条直线垂直，夹角为90度
else:
    # 计算两条直线的倾斜角（弧度）
    theta1 = np.arctan(slope1)
    theta2 = np.arctan(slope2)

    # 计算夹角（弧度），然后转换为度
    angle_rad = abs(theta1 - theta2)
    if angle_rad > math.pi / 2:  # 如果夹角大于90度，则计算补角
        angle_rad = math.pi - angle_rad
    angle = math.degrees(angle_rad)

print(f"第一条直线的斜率: {slope1}, 截距: {intercept1}")
print(f"第二条直线的斜率: {slope2}, 截距: {intercept2}")
print(f"两条直线之间的夹角: {angle}度")

# 可选：绘制结果
plt.scatter(points_group1[:, 0], points_group1[:, 1], color='blue', label='组1')
plt.scatter(points_group2[:, 0], points_group2[:, 1], color='red', label='组2')

x_fit1 = np.linspace(min(points_group1[:, 0]), max(points_group1[:, 0]), 10)
y_fit1 = slope1 * x_fit1 + intercept1
plt.plot(x_fit1, y_fit1, color='yellow', linestyle='--', label='拟合直线1')

x_fit2 = np.linspace(min(points_group2[:, 0]), max(points_group2[:, 0]), 10)
y_fit2 = slope2 * x_fit2 + intercept2
plt.plot(x_fit2, y_fit2, color='black', linestyle='--', label='拟合直线2')

plt.xlabel('X')
plt.ylabel('Y')
plt.title('两组点拟合成两条直线')
plt.legend()
plt.show()