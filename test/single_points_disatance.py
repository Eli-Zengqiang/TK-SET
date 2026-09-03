import  skspatial.objects as sko
import numpy as np
import open3d as o3d
# import matplotlib.pyplot as plt
import os
path=r"G:\TK-set\桃花\断面\断面/"
folds= os.listdir()
folders=[]
for fold in folds:
    folder=os.path.join(path,fold)
    folders.append(folder)

for folder in folders:
    points1=np.loadtxt(folder+"/点云.txt")[:, 0:3]
    points2=np.loadtxt(folder+"/点云2.txt")[:, 0:3]
    rows=points1.shape[0]

datas=np.zeros((rows,4))

for i in range(rows):
    point1=points1[i,:]
    point2=points2[i,:]
    point1=sko.Point(point1)
    point2=sko.Point(point2)
    distance=point1.distance(point2)
    datas[i,:]=[point1.x,point1.y,point1.z,distance]
