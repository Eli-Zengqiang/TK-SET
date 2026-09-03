import numpy as np
import math
import prism_ball.read_station_file as rf


#计算两个坐标的中间点
paths=r"E:\2.1SE-T32\2.1采集数据\20241024詹天佑\20241024001副本.txt"

def cacl_mean_point(path):
    number1=rf.read_station_points(path)
    nu=int(len(number1)/2)
    left_datas = np.empty((nu, 3))
    for i in range(0,nu):
        p0=number1[2*i]
        p1=number1[2*i+1]
        point_a=np.array(p0,dtype=float)
        point_b=np.array(p1,dtype=float)
        point_mean=(point_a+point_b)/2
        left_datas[i]=point_mean
    print(f"left_datas:{left_datas}")
    return left_datas
#两空间点形成向量
def calc_vector(point_b,point_a):
    # point_a=np.array(a)
    # point_b=np.array(b)
    vector_ab=point_b-point_a
    return vector_ab



# 计算两个平面的法向量的夹角
def calc_vector_angle(a,b):   #计算两个法向量的夹角
    #a=np.array([-0.00207534, -0.00164049, 0.999996])
    #b=np.array([0.935986, 0.351942, 0.00821074])
    # # 计算点积
    # dot_product = np.dot(vector_a, vector_b)
    # # 计算范数
    # norm_a = np.linalg.norm(vector_a)
    # norm_b = np.linalg.norm(vector_b)

    # # 计算夹角的余弦值
    # cos_theta = dot_product / (norm_a * norm_b)
    #
    # # 计算夹角（弧度）
    # theta_radians = np.arccos(cos_theta)
    a_vector=np.array(a)
    b_vector = np.array(b)

    cos_angle = np.dot(a_vector, b_vector) / (np.linalg.norm(a_vector) * np.linalg.norm(b_vector))
    radis = np.arccos(cos_angle)
    angle=radis * 180/math.pi
    return angle
    print(angle)


#a是新点 #b是以前四周点
# a=np.array([-0.479775, 0.877391, 0.000823471])# [16:32:35] 	- normal: (0.0899673, 0.995945, 0.000476414)
# b=np.array([-0.477706, 0.87852, 0.000682909])
# a=np.array([-0.0594889, -0.998222, 0.00362723])# 未搬站
# b=np.array([-0.0598566, -0.998199, 0.00407336]) #转棱镜球7
# a=np.array([-0.0760583, 0.997092, 0.00477434])# 未搬站
 #转棱镜球7

# hz=np.array([0, 0, 1])
#

#calc_vector_angle(b,c)
#calc_vector_angle(a,d)


def cacl_distance(x,y):
    np_x = np.array(x)
    np_y = np.array(y)
    distance=np.linalg.norm(np_x - np_y)
    return distance

#
# p0=[0.046,-0.7492,-0.1318] #棱镜坐标 设计参数
# p1=[0.046,0.7492,-0.1218] #棱镜坐标
# p0=[1.3211,11.9550,-0.332] #棱镜坐标  实际坐标
# p1=[-0.1740,12.0488,-0.3237] #棱镜坐标
#c=calc_vector(p0,p1)         #计算棱镜产生的向量
# #


d=[-0.0358031, -0.999359, 0.000792641]  #全站仪打点平面法向量[16:24:01]
# #雷达点云平面法向量

# calc_vector_angle(c,d)  #计算向量间夹角
# a1=5.373472586027925
# c1=[0.0388999, 0.999242, 0.00164327]
# e=[0.0248429, 0.999684, 0.00392946] #平面法向量
#calc_vector_angle(e,c1)
d=[-0.0358031, -0.999359, 0.000792641]  #全站仪打点平面法向量
point0=[1.5279,31.8663,5.5430] #全站仪墙上的点
point1=np.array(point0)
point_means=cacl_mean_point(paths)
vectors=np.empty((9,3))
angle_lists=[]
for i in range(len(point_means)):
    vector=calc_vector(point_means[i],point1)
    angle_list=calc_vector_angle(d,vector)
    angle_list1=round(angle_list,1)
    angle_lists.append(angle_list1)
print(f"采集入射角{angle_lists}")




