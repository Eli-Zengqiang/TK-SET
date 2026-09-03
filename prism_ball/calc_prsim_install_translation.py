import numpy as np
import prism_ball.read_station_file as rf
#计算法两个平面相交。返回直线（一个法向量，一个点p）


#计算法两个平面相交。返回直线（一个法向量，一个点p）
def Twoplaneintersection1(n,C):
    normal0 = np.array(n[0])
    normal1 = np.array(n[1])
    c0=np.array(C[0])
    c1 = np.array(C[1])
    normal=np.cross(normal0,normal1)
    planed0=np.dot(c0,normal0) #np.dot(c0,normal0) #15.938817799276693  n.X=d,n是法向量，X是直线上有点，nX的点积=d
    planed1= np.dot(c1,normal1)#np.dot(c1,normal1) #11.614901876392336
    # t0=np.array([0.468000,15.974000,-0.846000])
    # t1=np.array([1.484000,15.473000,-0.810000])
    # planed00=np.dot(t0,normal0)
    # planed11 = np.dot(t1, normal1)
    denom=np.dot(normal,normal)

    vector1= planed0*normal1 - planed1*normal0
    straight_p = np.cross(vector1, normal)/denom
    # straight_p=np.cross(vector1,normalized_vector)
    print(f'normal(计算该直线上的方向向量):{normal}')
    print(f'normalized_vector(计算该直线上的方向向量):{normalized_vector}')
    print(f'straight_p(计算该直线上的一个点):{straight_p}')

    return normal,straight_p

def check_point_in_line(norm,straight_p,Q,points_path):
    exdinct_array=np.zeros((1,3))
    d=0
    for id, point in enumerate(Q):
        point=np.array(point,dtype=float)
        straight_p=np.array(straight_p)
        PQ=point-straight_p
        t=np. dot(PQ,  norm) / np. dot( norm,  norm)
        check_point_on_line = straight_p + t * norm
        tolerance = 5e-3 # 设置一个小的误差范围,tolerance = 1e-10
        if np.allclose(point, check_point_on_line, atol=tolerance):
            if d==0:
                exdinct_array[0] =point
                d=d+1
            else:
                exdinct_array=np.vstack((exdinct_array,point))
                print("点Q在直线上")
        else:
            print("点Q不在直线上")
    print(exdinct_array)
    np.savetxt(points_path, exdinct_array,delimiter=',', fmt='%5f')
    return exdinct_array

def check_point_in_line1(straight_p,norm,path):
    #straight_p=np.array([0.72053413,10.75803696 ,0.29997616])
    #norm= np.array([-0.00473649,0.01917798,-0.67640246])#np.array([-0.00699952,0.02834083,-0.99957381])
    #print(norm)
    straight_p = np.array(straight_p)
    norm = np.array(norm)
    check_point_on_line0=np.zeros((1,3))
    for id,t in enumerate(np.arange(0,4,0.5)):
        check_point_on_line1= straight_p + t * norm
        check_point_on_line1=np.array(check_point_on_line1).reshape(1,-1)
        if id == 0:
            check_point_on_line0[id]=check_point_on_line1
        else:
            check_point_on_line0 = np.vstack((check_point_on_line0, check_point_on_line1))

    # print(check_point_on_line0)
    np.savetxt(path, check_point_on_line0, delimiter=',', fmt='%5f')
    return check_point_on_line0

def compute_plane_equation(paths):
    n=np.empty((2,3))
    C=np.empty((2,3))
    for id,path in enumerate(paths):
        # 计算质心
        points = np.loadtxt(path, delimiter=' ')[:, 0:3]
        C[id] = np.mean(points, axis=0)


        # 计算协方差矩阵
        Cov = np.cov(points.T)

        # 计算协方差矩阵的特征值和特征向量
        eigenvalues, eigenvectors = np.linalg.eigh(Cov)

        # 找到最小特征值对应的特征向量（法向量）
        n[id] = eigenvectors[:, np.argmin(eigenvalues)]

    # 计算常数 d
    # d = np.dot(n, C)
    # print("质心为:",C)
    # print("法向量:", n)
    # print("常数 d:", d)
    # print("平面方程:", f"{n[0]}x + {n[1]}y + {n[2]}z = {d}")
    print(f"质心:{C},法向量:{n}")
    return C,n

    # 示例点云数据（3D 坐标）
# points = np.loadtxt(r"E:\2.1SE-T32\2.1采集数据\20241025会堂计算角度\徕卡圆棱镜\左.txt",delimiter=' ')[:, 0:3]
# # points = np.array([
# #     [1, 2, 3],
# #     [2, 3, 4],
# #     [3, 4, 5],
# #     [4, 5, 6],
# #     # 可以添加更多点
# # ])
#
# # 计算平面方程
# n, d = compute_plane_equation(points)
# print("法向量:", n)
# print("常数 d:", d)
# print("平面方程:", f"{n[0]}x + {n[1]}y + {n[2]}z = {d}")


###########计算向量的归一化#################
def normalized_vector(vector):
    # 计算向量的L2范数（欧几里得长度）
    norm=np.linalg.norm(vector)
    # 进行归一化
    normalized_vector=vector/norm
    return normalized_vector


# def

if __name__=="__main__":

    #points = np.loadtxt(r"E:\2.1SE-T32\2.1采集数据\20241025会堂计算角度\徕卡圆棱镜\左.txt", delimiter=' ')[:, 0:3]
    paths=[r"E:\2.1SE-T32\2.1采集数据\20241025会堂计算角度\徕卡圆棱镜\2024-10-25_15-48-53\左侧.txt",r"E:\2.1SE-T32\2.1采集数据\20241025会堂计算角度\徕卡圆棱镜\2024-10-25_15-48-53\右侧.txt"]
    Q=rf.read_station_points(r"E:\2.1SE-T32\2.1采集数据\20241025会堂计算角度\徕卡圆棱镜\2024-10-25_15-58-55\周边相交线.txt")
    save_points_path = r"E:\2.1SE-T32\2.1采集数据\20241025会堂计算角度\徕卡圆棱镜\2024-10-25_15-58-55\交线错.txt"
    save_points_path1 = r"E:\2.1SE-T32\2.1采集数据\20241025会堂计算角度\徕卡圆棱镜\2024-10-25_15-48-53\output交线.txt"
    C,n = compute_plane_equation(paths)#获取质心和法向量
    norm,straight_p=Twoplaneintersection1(n,C)#计算平面交线的方向向量，和交线上一点

    check_point_in_line(norm,straight_p,Q,save_points_path)   #使用两个平面交线周边点进行验证
    check_point_in_line1(straight_p,norm,save_points_path1)
