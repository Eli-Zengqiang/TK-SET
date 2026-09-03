import numpy as np

datas=np.loadtxt(r"F:\2.1SE-T32\2.1采集数据\20250109\1.txt",delimiter=',')
print(datas)
a=np.array([1,2,3])
print(a)
dis=np.linalg.norm(a-datas[0,:])
print(dis)