import numpy as np
import transforms3d as tfs
import math

#设备的基准点云（转台中心，雷达的高度）-》全站仪坐标

TotalStationOffsetAngleZ=91.07282#设备与全站仪夹角
TotalStationOffsetVec=[0,0,0.2663]#设备与全站仪的平移
hz_mov_angle=0.462#正负还需要判断【设备激光笔需要单独标定的参数】
v_mov_angle=229.038#305.3对应90度，125.3对应了270度，0度相当于是35.3【设备激光笔需要单独标定的参数】
angle_z_x = 0.908#X,Y要交换【标定参数】
angle_z_y = 0.576#【标定参数】

def get_vec_angle(v0,v1):
    '''
    求两个向量的夹角
    :param v0:
    :param v1:
    :return:
    '''
    v0v1_dot = np.dot(v0,v1)
    v0_length = np.linalg.norm(v0)
    v1_length = np.linalg.norm(v1)
    cosValue = v0v1_dot / (v0_length * v1_length)
    angle = math.acos(cosValue)

    return angle

def rotation_matrix_rad(theta,axis):
    '''
    基于向量旋转指定角度
    :param theta: 旋转角
    :param axis: 向量
    :return: 
    '''
    c = math.cos(theta)
    s = math.sin(theta)
    xx = axis[0] * axis[0]
    yy = axis[1] * axis[1]
    zz = axis[2] * axis[2]
    xy = axis[0] * axis[1]
    yz = axis[1] * axis[2]
    xz = axis[0] * axis[2]
    
    xs = axis[0] * s
    ys = axis[1] * s
    zs = axis[2] * s
    
    M=np.zeros((3,3))
    M[0, 0] = xx*(1 - c) + c
    M[0, 1] = xy*(1 - c) - zs
    M[0, 2] = xz*(1 - c) + ys
    M[1, 0] = xy*(1 - c) + zs
    M[1, 1] = yy*(1 - c) + c
    M[1, 2] = yz*(1 - c) - xs
    M[2, 0] = xz*(1 - c) - ys
    M[2, 1] = yz*(1 - c) + xs
    M[2, 2] = zz*(1 - c) + c
    return M


def incMat(x_inc_angle,y_inc_angle,inc_angle=0):
    '''
    输入当前倾角仪的读数，输出旋转矩阵
    :param x_inc_angle:
    :param y_inc_angle:
    :return:
    '''
    #angle_z_x = -0.582#X,Y要交换
    #angle_z_y = 0.319
    #angle_z_x = 0.787#X,Y要交换【标定参数】
    #angle_z_y = -0.04#【标定参数】
    global angle_z_x,angle_z_y
    angle_0_x=y_inc_angle
    angle_0_y=x_inc_angle

    Gx_0 = math.cos(math.radians(90.0 - angle_0_x))
    Gy_0 = math.cos(math.radians(90.0 - angle_0_y))
    Gz_0 = math.sqrt(1 - Gx_0 * Gx_0 - Gy_0 * Gy_0)

    zAxisX_180 = math.cos(math.radians(90.0 - angle_z_x))
    zAxisY_180 = math.cos(math.radians(90.0 - angle_z_y))
    zAxisZ_180 = math.sqrt(1 - zAxisX_180 * zAxisX_180 - zAxisY_180 * zAxisY_180)

    InclinometerUpVec_0=np.array([Gx_0, Gy_0, Gz_0])#倾角传感器朝上的向量
    # mat_rz = tfs.euler.euler2mat(math.radians(0), math.radians(0), math.radians(inc_angle))#转回0度
    # InclinometerUpVec_0=np.dot(mat_rz,InclinometerUpVec_0)#全部统一到设备0度时的倾角传感器向量
    # print("转换为0度时倾角传感器的向量：",InclinometerUpVec_0)

    zAxis=np.array([zAxisX_180, zAxisY_180, zAxisZ_180])#偏移的向量

    #计算两个向量的变换矩阵
    #c = np.dot(InclinometerUpVec_0, zAxis)
    n_vector = np.cross(zAxis,InclinometerUpVec_0)
    n_vector = n_vector/np.linalg.norm(n_vector)
    n_vector=np.array([n_vector[0],n_vector[2],n_vector[1]])

    angle_rad=get_vec_angle(zAxis,InclinometerUpVec_0)
    print(angle_rad/np.pi*180)
    R_w2c=rotation_matrix_rad(angle_rad,n_vector)
    # print(c, n_vector)
    # n_vector_invert = np.array((
    #     [0, -n_vector[2], n_vector[1]],
    #     [n_vector[2], 0, -n_vector[0]],
    #     [-n_vector[1], n_vector[0], 0]
    # ))
    # I = np.eye(3)
    # # 核心公式：见上图
    # R_w2c = I + n_vector_invert + np.dot(n_vector_invert, n_vector_invert) / (1 + c)
    #print(R_w2c)

    return R_w2c

# angle_z_x=0.07
# angle_z_y=0.2905#-0.07
# print(incMat(1.126,2.128))#0度的时候  X,Y的读数
#
# angle_z_x=0.07
# angle_z_y=-0.07
# print(incMat(1.126,1.77))#0度X的读数 ，270度的时候X的读数
# 1.77+0.07  ==  2.128-0.2905


def device_2_geo(point,tps_point=[0.0, 0.0, 0.0],geo_angle=0):
    #输入的geo_angle
    rz_mat=tfs.euler.euler2mat(math.radians(0),math.radians(0),math.radians(TotalStationOffsetAngleZ))#设备与全站仪的旋转
    rz_mat_geo=tfs.euler.euler2mat(math.radians(0),math.radians(0),math.radians(geo_angle))#全站仪自身的旋转角
    point=np.array(point)
    new_point=rz_mat.dot(point)+np.array(TotalStationOffsetVec)
    new_point=np.dot(rz_mat_geo,new_point)+np.array(tps_point)
    print(new_point)
#device_2_geo([-2.795,0.083,0.91],geo_angle=-(129+13/60+47/3600))#输入：-2.795,0.083,0.91，输出-1.903,2.049,1.175
def geo_2_device(point,tps_point=[490541.6665, 3302380.3726, 1315.8169],geo_angle=0):
    '''
    将点从全站仪坐标系转换到设备坐标系
    :param point:施工坐标系的点
    :param geo_angle:全站仪当前的旋转角度HZ
    :return:
    '''
    global TotalStationOffsetAngleZ,TotalStationOffsetVec
    rz_mat=tfs.euler.euler2mat(math.radians(0),math.radians(0),math.radians(TotalStationOffsetAngleZ))#设备与全站仪的旋转【标定参数】
    rz_mat_geo=tfs.euler.euler2mat(math.radians(0),math.radians(0),math.radians(geo_angle))#全站仪自身的旋转角【//APP输入参数】
    point = np.array(point)#【//APP输入参数】
    new_point = point - np.array(tps_point)#【//APP输入参数】
    new_point=np.dot(np.linalg.inv(rz_mat_geo),new_point)
    new_point=new_point-np.array(TotalStationOffsetVec)#高程【标定参数】
    new_point = np.dot(np.linalg.inv(rz_mat), new_point)
    print(new_point)
    return new_point
#geo_2_device([-1.905,2.046,1.1763],tps_point=[0.0,0.0,0.0],geo_angle=-(129+13/60+47/3600))

#print(np.arctan(0.108/5.79)/np.pi*180/2)




def get_need_hv(global_point):
    '''
    输入scanpoint的点，输出需要旋转的角度
    :param global_point:设备坐标系下的点
    :return:
    '''
    LaserOffsetVec = [0.0, 0.036, 0.0]#激光笔的位置【设备激光笔需要单独标定的参数】
    globalX,globalY,globalZ=global_point[0],global_point[2],global_point[1]
    TPS_X, TPS_Y, TPS_Z = LaserOffsetVec

    VectorX = globalX - TPS_X
    VectorY = globalY - TPS_Y
    VectorZ = globalZ - TPS_Z

    r = math.sqrt(VectorX * VectorX + VectorY * VectorY + VectorZ * VectorZ)
    tv = math.acos(VectorZ / r) # 竖直角弧度
    #thz = math.atan(VectorY / VectorX) # 水平角弧度
    thz = math.acos(VectorX / math.sqrt(VectorX * VectorX + VectorY * VectorY))
    #thz=thz
    print("thz:",thz/math.pi*180)
    if  VectorY < 0:
        thz = math.pi + thz
    if VectorY > 0:
        thz = math.pi - thz
    return thz/math.pi*180,tv/math.pi*180


def point_to_hv(point=[-1.69,1.315,-5.02],zero_inc=[2.822,-4.779]):
    '''
    #从已经摆水平的局部点云，选择点，然后控制设备找点
    :param point:水平的局部点云，选择点
    :param zero_inc:0度时的倾角仪器读数
    :return:
    '''
    point=np.array([point[0],point[2],point[1]])#选取的点需要将Y,Z反过来

    #计算当前倾角的旋转矩阵：
    mat=incMat(zero_inc[0],zero_inc[1])#0度的倾角仪读数【需要读取的参数】
    new_point=np.dot(np.linalg.inv(mat),point)#还原到设备坐标系下的点
    hz,v=get_need_hv(new_point)#计算hz,v
    print(hz,v)
    return hz,v



def geo_point_to_hv(geo_point,tps_point,geo_angle=0,zero_inc=[2.822,-4.779]):
    '''
    从全站仪坐标系的点转换成小电机转动参数
    :param geo_point:全站仪坐标系待指点的点
    :param tps_point:全站仪 设站坐标
    :param geo_angle:采集时全站仪的水平偏角
    :param zero_inc:0度时的倾角仪读数
    :return:
    '''
    geo_point = np.array(geo_point)
    new_point=geo_2_device(geo_point,tps_point,-geo_angle)#这个方法输入的角度要取反
    hz,v=point_to_hv(new_point,zero_inc)
    #根据hz,v 算出两个电机需要转到的位置
    # 这里只对全站仪把手角度进行了补偿
    end_hz=hz+hz_mov_angle+(TotalStationOffsetAngleZ-90)
    if end_hz>360:
        end_hz-=360
    if end_hz<0:
        end_hz+=360
    end_v=v+v_mov_angle
    #print(end_hz,end_v)
    return end_hz,end_v



#[1.886,  5.706,   2.049]
#[-1.804,  5.727,   1.901]

point_list=[[1.861999988556,5.748000144958,2.375999927521],
[0.234999999404,5.688000202179,1.315999984741],
[-0.291000008583,5.710999965668,1.309999942780],
[-1.804000020027,5.727000236511,1.901000022888],
[1.970999956131,4.013999938965,0.273000001907],
[1.962000012398,-1.194000005722,1.661000013351],
[-0.395999997854,-1.912999987602,1.759999990463],
[-1.815999984741,-1.894000053406,1.098000049591],
[-1.802999973297,-1.021000027657,1.881999969482]]
out_list=[]
for point in point_list:
    end_hz,end_v=geo_point_to_hv(point,[0.0,0.0,0.0],geo_angle=178+47/60+3/3600,zero_inc=[0.695,2.14])
    out_list.append([end_hz,end_v])

print("---------------\n",out_list)