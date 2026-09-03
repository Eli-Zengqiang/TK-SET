# import numpy as np
#
#
# def calculate_horizontal_projection_angle(n1, n2):
#     # n1和n2是两个平面的法向量，格式为(x, y, z)
#     # 计算在XY平面上的投影
#     proj_n1 = np.array([n1[0], n1[1], 0])
#     proj_n2 = np.array([n2[0], n2[1], 0])
#
#     # 避免零向量的情况
#     if np.linalg.norm(proj_n1) == 0 or np.linalg.norm(proj_n2) == 0:
#         return "Projection is a zero vector"
#
#         # 计算投影向量的点积和模长
#     dot_product = np.dot(proj_n1, proj_n2)
#     norm_n1 = np.linalg.norm(proj_n1)
#     norm_n2 = np.linalg.norm(proj_n2)
#
#     # 计算夹角（以弧度为单位）
#     angle_rad = np.arccos(dot_product / (norm_n1 * norm_n2))
#     # 转换为度
#     angle_deg = np.degrees(angle_rad)
#
#     # 返回角度（度）
#     return angle_deg
#
#
# # 示例：两个平面的法向量
# n1 = (-0.479775, 0.877391, 0.000823471)
# n2 = (-0.477706, 0.87852, 0.000682909)
#
# # 计算夹角
# angle = calculate_horizontal_projection_angle(n1, n2)
# print(f"The angle between the projections of the two planes' normals on the XY plane is: {angle:.6f} degrees")

import math


def calculate_angle(x1, y1, x2, y2, x3, y3, x4, y4):
    # 计算向量
    vec_p = (x2 - x1, y2 - y1)
    print(vec_p)
    vec_q = (x4 - x3, y4 - y3)
    print(vec_q)
    # 计算点积和模
    dot_product = vec_p[0] * vec_q[0] + vec_p[1] * vec_q[1]
    mag_p = math.sqrt(vec_p[0] ** 2 + vec_p[1] ** 2)
    mag_q = math.sqrt(vec_q[0] ** 2 + vec_q[1] ** 2)

    # 计算夹角的余弦值
    cos_theta = dot_product / (mag_p * mag_q)

    # 计算夹角（转换为度）
    theta_radians = math.acos(cos_theta)
    theta_degrees = math.degrees(theta_radians)
    print(theta_degrees)

    return theta_degrees


# 示例
x1=16.641001
y1=3.122000
x2=13.119000
y2=9.280000
x3=15.853000
y3=4.315000
x4=12.565000
y4=-10.730000
calculate_angle(x1, y1, x2, y2, x3, y3, x4, y4)
