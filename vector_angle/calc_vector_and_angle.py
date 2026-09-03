import numpy as np
import math

def calc_vector(a,b):
    point_a=np.array(a)
    point_b=np.array(b)
    vector_ab=point_b-point_a
    return vector_ab

# 计算两个平面的法向量的夹角
def calc_vector_angle(a,b):   #计算两个法向量的夹角
    a_vector = np.array(a)
    b_vectors = np.array(b)

    cos_angle = np.dot(a_vector, b_vectors) / (np.linalg.norm(a_vector) * np.linalg.norm(b_vectors))
    radis = np.arccos(cos_angle) #计算弧度值
    angle=radis * 180/math.pi #计算角度值
    print("对应法向量与全站仪角度为：",angle)



def cacl_distance(x,y):   #计算两个三维点的距离
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


if __name__=="__main__":
    c = [0.999782, -0.0207806, 0.00189398]
    d = [0.0230711, 0.999727, 0.00371466]
    calc_vector_angle(c, d)  # 计算两个向量间夹角
    # cacl_distance(x, y)    #计算两点的距离
    # c=calc_vector(p0,p1)   #计算两点形成的向量

# rad=math.atan(0.017/10)
# angle=rad/(math.pi)*180
# print(angle)