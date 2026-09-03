import os

import skspatial.objects as sko
import numpy as np
import open3d as o3d
a=[]
file_path=r"E:\2.1SE-T32\2.1采集数据\CE56\all_inc2.txt"
fold = r"E:\2.1SE-T32\2.1采集数据\CE56\2024-06-24_10-31-28-inc2/" #件夹路径
#fold=r"C:\Users\ZHXR\Desktop\20240524-CF52/"
knn_n=30 #计算点个数（如coludecomare 计算时的6points
points_TS_str=0   #1是第一列为非数据 0是直接第一列为数据
#TS_files =['20240507008-1']
TS_files =['四周','高处','楼顶部','地面']
#TS_files =['1号墙壁','2号墙壁','3号墙壁','4号墙壁','创新1号面','创新2号面','创新高程顶部']

start_inc=0
end_inc=0.49
step=0.01
#PC_file='AllGeoPoints_inc_0.4.txt'
inc_range=np.arange(start_inc,end_inc,step)

for inc in inc_range:
    PC_file = f'AllGeoPoints_inc_{round(inc,3)}.txt'

    points_PC = np.loadtxt(fold + PC_file)[:, 0:3]
    pc_PC = o3d.geometry.PointCloud()  # type:open3d.cpu.pybind.geometry.PointCloud
    pc_PC.points = o3d.utility.Vector3dVector(points_PC)
    pcd_tree = o3d.geometry.KDTreeFlann(pc_PC)
    points_TS_all=np.empty([0,4])
    for TS_file in TS_files:
        if points_TS_str:
            points_TS_str = np.loadtxt(fold + TS_file+'.txt', dtype=str, delimiter=',')
            ind = np.where(points_TS_str[:, 1] != '')[0]
            points_TS = np.ones([len(ind), 4])
            points_TS[:, 0:3] = points_TS_str[ind, 1:4].astype(float)
        else:
            points_TS= np.loadtxt(fold + TS_file+'.txt')[:, 0:3]
            points_TS = np.ones([len(points_TS[:,1]), 4])
            points_TS[:, 0:3] = np.loadtxt(fold + TS_file+'.txt')[:, 0:3]
        for i in range(len(points_TS)):
            [_, ind, _] = pcd_tree.search_knn_vector_3d(points_TS[i,0:3], knn_n)
            neibr_points = np.asarray(pc_PC.points)[ind]
            plane = sko.Plane.best_fit(neibr_points)
            points_TS[i,3]=plane.distance_point_signed(points_TS[i,0:3])
        scan_dist=np.linalg.norm(points_TS[:,0:3],axis=1).mean()
        #print(type(str(round(scan_dist,1))))
        points_TS_all=np.append(points_TS_all,points_TS)

        print(TS_file+'('+str(round(scan_dist,1))+')最大绝对距离：'+str(np.abs(points_TS[:,3]).max())+';平均距离：'+str(points_TS[:,3].mean())+';标准差：'+str(points_TS[:,3].std()))#points_TS[:,3]

        with open(file_path,'a+',encoding='utf-8') as f:
            f.write(f"inc:{round(inc, 3)}:{TS_file}{round(scan_dist,1)} 最大绝对距离:{(np.abs(points_TS[:,3]).max())} 平均距离:{points_TS[:,3].mean()} 标准差:{(points_TS[:,3].std())}\n")



